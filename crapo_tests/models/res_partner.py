"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""
import logging

from odoo import models, api
from odoo.addons.crapo_automaton.mixins import crapo_automata_mixins
from odoo.addons.crapo_workflow.trigger import wf_trigger


class ResPartnerWithMixin(
    crapo_automata_mixins.ObjectWithStateMixin, models.Model
):
    _inherit = "res.partner"

    @api.multi
    def write(self, values):
        res = super(ResPartnerWithMixin, self).write(values)
        self.wf_trigger("record_write")
        return res

    @api.model
    def create(self, values):
        rec = super(ResPartnerWithMixin, self).create(values)
        rec.wf_trigger("record_create")
        return rec
