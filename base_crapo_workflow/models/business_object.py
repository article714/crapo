# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID
from odoo import fields, models, _, exceptions


class WorkflowBusinessObject(models.Model):
    """
    Base class to define a Business Object.

    Should be use as a mixin class in existing objects
    """
    _name = 'crapo.business.object'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u"An object on which to  in a workflow, specific to a given model"

    state = fields.Many2one(comodel_name='crapo.state',
                            string=_(u'State'),
                            help=(u"""State in which this object is"""),
                            track_visibility='onchange',
                            domain=lambda self: self._get_state_domain(),
                            group_expand='_read_group_states',
                            default=lambda self: self._default_state(),  store=True, index=True, required=True)

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
            return [('model_id', '=', self.my_model_ref.id)]
        else:
            my_model = self._get_my_model_ref()
            return [('model_id', '=', my_model.id)]

    def _default_state(self):
        return self.env['crapo.state'].search(self._get_state_domain(), limit=1)

    def _next_state_id(self):
        self.ensure_one()
        next_state = self._next_state()
        if next_state:
            return next_state.id
        else:
            return -1

    def _next_state(self):
        self.ensure_one()
        domain = self._get_state_domain()
        domain.append(('sequence', '>', self.state.sequence))
        next_state = self.env['crapo.state'].search(domain, limit=1)
        if next_state:
            return next_state[0]
        else:
            return None

    def _read_group_states(self, states, domain, order):
        search_domain = self._get_state_domain(domain=domain)
        state_ids = states._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return states.browse(state_ids)
