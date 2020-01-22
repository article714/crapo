# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, api
from odoo.addons.queue_job.job import job
from odoo.tools.safe_eval import safe_eval


class WorkflowBroker(models.TransientModel):
    """
        A trigger step in a Workflow
    """

    _name = "crapo.workflow.broker"

    @job
    @api.model
    def notify(self, event_type, values):

        record = values["record"]

        domain = [
            ("event_type", "=", event_type),
            ("model_id", "=", self.env["ir.model"]._get_id(record._name),),
        ]
        context = {"env": self.env, "values": values}

        # Looking for event concerned
        for rec_event in self.env["crapo.workflow.event"].search(domain):

            if rec_event.trigger_id.init_trigger and (
                not rec_event.condition
                or safe_eval(rec_event.condition, context,)
            ):
                new_ctx = self.env["crapo.workflow.context"].create(
                    {
                        "workflow_id": rec_event.trigger_id.workflow_id.id,
                        "context_event_status_ids": [
                            (0, False, {"event_id": rec_event.id,},)
                        ],
                    }
                )
                new_ctx.set_context_entry(
                    rec_event.trigger_id.init_record_key, record
                )
                new_ctx.context_event_status_ids[0].write({"done": True})
            else:

                for rec_status in rec_event.context_event_status_ids:
                    context["wf"] = rec_status.wf_context_id

                    if (
                        not rec_event.record_id_context_key
                        or rec_status.record_id == record.id
                    ) and (
                        not rec_event.condition
                        or safe_eval(rec_event.condition, context,)
                    ):
                        rec_status.write({"done": True})
