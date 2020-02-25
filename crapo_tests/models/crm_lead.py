"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)
@author: D. Couppé (Article 714)

"""

from odoo import models


class CrmLeadWithMixin(models.Model):
    """
        Add crapo.automaton.mixin on crm.lead model
    """

    _inherit = ["crm.lead", "crapo.automaton.mixin"]
    _name = "crm.lead"
