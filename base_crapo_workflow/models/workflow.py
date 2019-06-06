# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class WorkflowWorkflow(models.Model):
    """
    A workflow coordinates and automates a set of workflow activities that
    can apply to a whole set of business objects
    """

    _name = "crapo.workflow"
    _description = """ Specification of a Crapo Workflow, a set of Activities,
    Triggers, Events and WFTransitions"""

    name = fields.Char(
        string="Name", help="Workflow's name", required=True, translate=True
    )

    activities = fields.One2many("crapo.workflow.activity", inverse_name="workflow")

    transitions = fields.One2many(
        comodel_name="crapo.workflow.transition", inverse_name="workflow"
    )
