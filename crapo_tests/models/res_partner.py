"""
See README for details
"""
from odoo import models, api


class ResPartner(models.Model):
    """
        Add crapo.automaton.mixin to res.partner and emit wf_event
        on event and create
    """

    _inherit = ["res.partner", "crapo.automaton.mixin"]
    _name = "res.partner"

    @api.model
    def create(self, values):
        """
            Emit wf_event on create
        """
        rec = super(ResPartner, self).create(values)
        rec.wf_event("record_create")
        return rec

    @api.multi
    def write(self, values):
        """
            Emit wf_event on write
        """
        res = super(ResPartner, self).write(values)
        self.wf_event("record_write")
        return res
