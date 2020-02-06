# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    usage = fields.Selection(
        selection_add=[("crapo_workflow_activity", "Crapo workflow activity")]
    )


class WorkflowActivity(models.Model):
    """
    An activity step in a Workflow, i.e. a step where something must be done
    """

    _name = "crapo.workflow.activity"
    _inherits = {"ir.actions.server": "action_server_id"}
    _description = (
        "Workflow activity: a specialization of server actions for Crapo"
    )

    action_server_id = fields.Many2one(
        "ir.actions.server", required=True, ondelete="restrict"
    )

    workflow_id = fields.Many2one("crapo.workflow", ondelete="cascade")

    record_context_key = fields.Char()

    @job
    @api.multi
    def run(self, wf_context_id):
        """
            Runs the server action, possibly in async and add some values to context
        """

        context = {"wf": wf_context_id, "logging": logging}

        res = False
        for rec in self:
            if rec.record_context_key:
                active_record = wf_context_id.get_context_entry(
                    rec.record_context_key
                )
                context["active_id"] = active_record.id
                context["active_model"] = active_record._name

            res = rec.with_context(**context).action_server_id.run()
            rec.wf_event("on_activity_ended")
        return res

    # ==============================
    # Write/Create
    # ==============================

    @api.model
    def create(self, values):
        values["usage"] = "crapo_workflow_activity"
        return super(WorkflowActivity, self).create(values)
