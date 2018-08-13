# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions


class StateMachineTransition(models.Model):
    """
    A transition between two states
    """
    _name = 'crapo.transition'

    name = fields.Char(string=_(u'Name'),
                       help=_(u"Transition's name"), required=True, translate=True)

    preconditions = fields.Char(string=_(u"Pre-conditions"), help=_(u"Conditions to be checked before initiating this transition"),
                                required=False)

    postconditions = fields.Char(string=_(u"Post-conditions"), help=_(u"Conditions to be checked before ending this transition"),
                                 required=False)

    automaton = fields.Many2one(string="Automaton",
                                comodel_name='crapo.automaton',
                                default=lambda self: self._get_default_automaton(),
                                store=True, required=True, index=True)

    model_id = fields.Many2one(string=_(u'Model'),
                               comodel_name="ir.model",
                               related='automaton.model_id'
                               )

    from_state = fields.Many2one(string='From state',
                                 comodel_name='crapo.state')

    to_state = fields.Many2one(string='To state',
                               comodel_name='crapo.state')

    action = fields.Many2one(string=_(u'Action to be executed when transitioning'),
                             comodel_name='ir.actions.server',  domain=lambda self: self._get_action_domain(), required=False)

    def _get_action_domain(self):
        if self.model_id:
            return [('model_id', '=', self.model_id.id)]
        return []

    def _get_default_automaton(self):
        default_value = 0
        if 'current_automaton' in self.env.context:
            try:
                default_value = int(self.env.context.get('current_automaton'))
            except:
                default_value = 0

        return self.env['crapo.automaton'].browse(default_value)
