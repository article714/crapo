# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo import fields, models, _, api, exceptions


class WorkflowBusinessObject(models.Model):
    _name = 'workflow.object'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u"An object on which to  in a workflow, specific to a given model"

    state = fields.Many2one(comodel_name='workflow.state',
                            string=_(u'State'),
                            help=(u"""State in which this object is"""),
                            track_visibility='onchange',
                            domain=lambda self: self._get_state_domain(),
                            group_expand='_read_group_states',
                            default=lambda self: self._default_state(),  store=True, index=True, required=True)

    # State Management
    def _get_state_domain(self, domain=None):
        return [('model_id', '=', self.model.id)]

    @api.model
    def _default_state(self):
        return self.env['workglow.state'].search(self._get_state_domain(), limit=1)

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
        next_state = self.env['workflow.state'].search(domain, limit=1)
        if next_state:
            return next_state[0]
        else:
            return None

    @api.model
    def _read_group_states(self, states, domain, order):
        search_domain = self._get_state_domain(domain=domain)
        state_ids = states._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return states.browse(state_ids)
