"""
See README for details
"""

from odoo import models


class CrmLeadWithMixin(models.Model):
    """
        Add crapo.automaton.mixin on crm.lead model
    """

    _inherit = ["crm.lead", "crapo.automaton.mixin"]
    _name = "crm.lead"
