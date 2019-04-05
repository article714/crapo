# coding: utf-8

"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins


class CrmLeadWithMixin(crapo_automata_mixins.WrappedStateMixin,models.Model):
    _inherit = "crm.lead"
