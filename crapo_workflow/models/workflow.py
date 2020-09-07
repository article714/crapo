"""
see README for details
"""
from odoo import models, fields


class Workflow(models.Model):
    """
        A workflow coordinates and automates a set of workflow activities that
        can apply to a whole set of business objects
    """

    _name = "crapo.workflow"
    _description = """ Specification of a Crapo Workflow, a set of Activities,
    Triggers, Events and WFTransitions"""

    name = fields.Char(help="Workflow's name", required=True)
