# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID
from odoo import fields, models, _, exceptions, api
from odoo.tools.safe_eval import safe_eval


class WorkflowBusinessObject(models.Model):
    """
    Base class to define a Business Object.

    Should be use as a mixin class in existing objects
    """
    _name = 'crapo.business.object'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u"An object on which to  in a workflow, specific to a given model"

    state = fields.Many2one(comodel_name='crapo.state',
                            string=_(u'State'),
                            help=(u"""State in which this object is"""),
                            track_visibility='onchange',
                            domain=lambda self: self._get_state_domain(),
                            group_expand='_read_group_states',
                            default=lambda self: self._default_state(), store=True, index=True, required=True)

    automaton = fields.Many2one(comodel_name='crapo.automaton',
                                string=_(u'Related automaton'),
                                help=(u"""The automaton describes the various transition an object can go through between states"""),
                                related='state.automaton',
                                store=True, index=True, required=False)

    my_model_ref = fields.Many2one(comodel_name='ir.model',
                                   string=_("My model"),
                                   help=_("A reference to current object's Model, used to help retrieve dynamic states"),
                                   compute="_get_my_model_ref",
                                   domain=lambda self: self._get_my_model_ref(True),
                                   default=lambda self: self._get_my_model_ref(),
                                   store=True, index=True, required=True)

    # Reference to My Model:
    def _get_my_model_ref(self, domain=False):
        my_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        for record in self:
            record.my_model_ref = my_model
        if domain:
            return [('model_id', '=', my_model.id)]
        else:
            return my_model

    # State Management
    def _get_state_domain(self, domain=None):

        if self.my_model_ref:
            result = [('model_id', '=', self.my_model_ref.id)]
        else:
            my_model = self._get_my_model_ref()
            result = [('model_id', '=', my_model.id)]

        if self.automaton:
            result.append(('automaton', '=', self.automaton.id))

        return result

    def _default_state(self):
        domain = self._get_state_domain()

        if self.automaton:
            domain.append('|', ('is_start_state', '=', True), ('default_state', '=', 1))

        return self.env['crapo.state'].search(domain, limit=1)

    def _next_states(self):
        self.ensure_one()
        domain = self._get_state_domain()
        next_states = False
        if self.automaton:
            eligible_transitions = self.env['crapo.transition'].search(
                [('automaton', '=', self.automaton.id), ('from_state', '=', self.state.id)])
            target_ids = eligible_transitions.mapped(lambda x: x.to_state.id)

            if target_ids:
                domain.append(('id', 'in', target_ids))

                next_states = self.env['crapo.state'].search(domain)

        else:
            domain.append(('sequence', '>', self.state.sequence))
            next_states = self.env['crapo.state'].search(domain, limit=1)

        return next_states

    def _read_group_states(self, states, domain, order):
        search_domain = self._get_state_domain(domain=domain)
        state_ids = states._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return states.browse(state_ids)

    @api.multi
    def write(self, values):
        """
        we override write method in order to preventing transitioning to a non eligible state
        """
        # Look for a change of state
        target_state_id = None
        result = True

        if "state" in values:
            target_state_id = values["state"]

        # check if there is a change state needed
        if target_state_id != None:

            # Check if next state is valid
            for record in self:
                if record.state and target_state_id:
                    next_states = record._next_states()
                    if not next_states:
                        raise exceptions.ValidationError(_(u"No target state is elegible for transitionning"))
                    if not target_state_id in next_states.ids:
                        raise exceptions.ValidationError(_(u"State is not in eligible target states"))

            # Search for elected transition
            transition_elected = self.env['crapo.transition'].search(
                [('from_state', '=', self.state.id), ('to_state', '=', target_state_id)], limit=1)

            if transition_elected:
                is_valid = True
                result = True

                if transition_elected.write_before:
                    result = super(WorkflowBusinessObject, self).write(values)

                # Test preconditions
                if transition_elected.preconditions:
                    for obj in self:
                        try:
                            is_valid = safe_eval(transition_elected.preconditions, {'object': obj, 'env': self.env})
                        except Exception as e:
                            logging.error(u"CRAPO: Failed to validate transition preconditions: %s", str(e))
                            is_valid = False

                        # Raise an error if not valid
                        if not is_valid:
                            raise exceptions.ValidationError(
                                u"Invalid Pre-conditions for Object: %s" % obj.display_name)

                # Should we go for it?
                if is_valid and transition_elected.action:
                    # does action needs to be taken asynchronously?
                    action = self.env['crapo.action'].browse(transition_elected.action.id)
                    context = {
                        'active_model': self._name,
                        'active_id': self.id,
                        'active_ids': self.ids
                    }
                    if action:
                        if transition_elected.async_action:
                            action.with_delay().run_async(context)
                        else:
                            action.with_context(context).run()

                # Test postconditions if action is not asynchronous
                if transition_elected.postconditions and not transition_elected.async_action:
                    for obj in self:
                        try:
                            is_valid = safe_eval(transition_elected.postconditions, {'object': obj, 'env': self.env})
                        except Exception as e:
                            logging.error(u"CRAPO: Failed to validate transition postconditions: %s", str(e))
                            is_valid = False
                        # Raise an error if not valid
                        if not is_valid:
                            raise exceptions.ValidationError(
                                u"Invalid Post-conditions for Object: %s" % obj.display_name)
                # writing after id needed
                if not transition_elected.write_before:
                    result = super(WorkflowBusinessObject, self).write(values)

                return result

        else:
            return super(WorkflowBusinessObject, self).write(values)
