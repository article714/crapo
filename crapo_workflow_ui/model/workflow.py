from odoo import models, fields


class Workflow(models.Model):
    """
        Added some One2many to crapo.wokrflow for UI convenience
    """

    _inherit = "crapo.workflow"

    activity_ids = fields.One2many("crapo.workflow.activity", "workflow_id")

    trigger_ids = fields.One2many("crapo.workflow.trigger", "workflow_id")

    context_ids = fields.One2many("crapo.workflow.context", "workflow_id")

    node_ids = fields.One2many("crapo.workflow.diagram.node", "workflow_id")
