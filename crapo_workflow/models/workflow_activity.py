# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class IrActionsServer(models.Model):
    """
        Inerhit from ir.actions.server to add
        some usage and object to eval context
    """

    _inherit = "ir.actions.server"

    DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the activity is triggered
#  - model: Odoo Model of the record on which the activity is triggered; is a void recordset
#  - record: record linked to active record context key; may be void
#  - records: recordset of all records on which the activity is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
#  - wf_context: record of crapo workflow context that triggered this activity
#  - logging: python logging module helpfull to debug
# To return an action, assign: action = {...}\n\n\n\n"""

    usage = fields.Selection(
        selection_add=[("crapo_workflow_activity", "Crapo workflow activity")]
    )

    code = fields.Text(default=DEFAULT_PYTHON_CODE)

    @api.model
    def _get_eval_context(self, action=None):
        """
            Add wf_context to eval context
        """
        eval_context = super(IrActionsServer, self)._get_eval_context(
            action=action
        )

        eval_context.update(
            {
                "logging": logging,
                "wf_context": self.env.context["wf_context_id"],
            }
        )
        return eval_context


class WorkflowActivity(models.Model):
    """
        An activity step in a Workflow, all of what is done in ir.server.actions
        can be done in WorkflowActivity
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

    active_record_context_key = fields.Char()

    @job
    @api.multi
    def run(self, wf_context_id):
        """
            Runs the server action, possibly in async and add some values to context
        """

        context = {"wf_context_id": wf_context_id}

        res = False
        for rec in self:
            if rec.active_record_context_key:
                active_record = wf_context_id.get_context_entry(
                    rec.active_record_context_key
                )
                context["active_id"] = active_record.id
                context["active_model"] = active_record._name

            res = rec.with_context(**context).action_server_id.run()
            rec.wf_event(
                "activity_ended", {"activity_wf_ctx_id": wf_context_id}
            )
        return res

    # ==============================
    # Write/Create
    # ==============================

    @api.model
    def create(self, values):
        values["usage"] = "crapo_workflow_activity"
        return super(WorkflowActivity, self).create(values)
