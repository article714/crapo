# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class WorkflowActivity(models.Model):
    """
    An activity step in a Workflow, i.e. a step where something must be done
    """

    _name = "crapo.workflow.activity"
    _inherit = "ir.actions.server"
    _description = (
        u"Workflow activity: a specialization of server actions for Crapo"
    )

    workflow = fields.Many2one("crapo.workflow")

    # Multi
    child_ids = fields.Many2many(
        "crapo.workflow.activity", "rel_crapo_actions"
    )

    @api.multi
    @job
    def run_async(self, context={}):  # pylint: disable=dangerous-default-value
        self.with_context(context).run()
