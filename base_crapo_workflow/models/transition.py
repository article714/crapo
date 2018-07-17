# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions


class WorkflowTransition(models.Model):
    _name = 'workflow.transition'

    name = fields.Char(string=_(u'Name'),
                       help=_(u"Transition's name"), required=True, translate=True)

    preconditions = fields.Char(string=_(u"Pre-conditions"), help=_(u"Conditions to be checked before initiating this transition"),
                                required=False)

    postconditions = fields.Char(string=_(u"Post-conditions"), help=_(u"Conditions to be checked before ending this transition"),
                                 required=False)

    def _get_action_domain(self):
        lot_model = self.env['ir.model'].search([('model', '=', 'dynalec.lot')])
        if lot_model != None and lot_model:
            model_id = lot_model.id
            if model_id:
                return [('model_id', '=', model_id)]
        return []

    action = fields.Many2one(string=_(u'Action to be executed when transitioning'),
                             comodel_name='ir.actions.server', domain=_get_action_domain, required=False)
