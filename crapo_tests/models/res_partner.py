"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""

from odoo import models, api


class ResPartnerWithMixin(models.Model):
    _inherit = ["res.partner", "crapo.automaton.mixin"]
    _name = "res.partner"

    @api.multi
    def write(self, values):
        res = super(ResPartnerWithMixin, self).write(values)
        self.wf_event("record_write")
        return res

    @api.model
    def create(self, values):
        rec = super(ResPartnerWithMixin, self).create(values)
        rec.wf_event("record_create")
        return rec
