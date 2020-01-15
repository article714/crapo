# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class WorkflowActivity(models.Model):
    """
    An activity step in a Workflow, i.e. a step where something must be done
    """

    _name = "crapo.workflow.activity"
    _inherit = "ir.actions.server"
    _description = (
        "Workflow activity: a specialization of server actions for Crapo"
    )

    workflow_id = fields.Many2one("crapo.workflow")

    @job
    @api.multi
    def run(self, wf_context_id):
        """
            Runs the server action, possibly in async and add some values to context
        """

        context = {"wf": wf_context_id, "logging": logging}

        res = False
        for rec in self.with_context(**context):
            res = super(WorkflowActivity, rec).run()
            rec._event("on_activity_ended").notify(rec)

        return res
