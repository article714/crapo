"""
see README for details
"""
from odoo import models, api
from odoo.addons.queue_job.job import job
from odoo.tools.safe_eval import safe_eval


class WorkflowBroker(models.TransientModel):
    """
        The broker will receive all the event notification
        and evaluate them
    """

    _name = "crapo.workflow.broker"

    @job
    @api.model
    def notify(self, event_type, values):
        """
            Call by method wf_event from base model to receive and
            evaluate event.

            * values must content a key 'record' that contain the record
            that throws the event
        """
        # Record asssociate with this event
        record = values["record"]

        # Build a context for later safe_eval with env and values content
        context = {"env": self.env}
        context.update(values)

        domain = [
            ("event_type", "=", event_type),
            (
                "model_id",
                "=",
                self.env[  # pylint: disable=protected-access
                    "ir.model"
                ]._get_id(
                    record._name  # pylint: disable=protected-access
                ),
            ),
        ]

        # Get empty recordset to accumulate done wf_ctx_event
        done_ctx_event = self.env["crapo.workflow.context.event"]

        # Looking for event concerned
        for rec_event in self.env["crapo.workflow.event"].search(domain):
            # If event belongs to an init trigger, and its condition
            # is met then create a new workflow context
            if rec_event.trigger_id.trigger_type == "init" and (
                not rec_event.condition
                or safe_eval(rec_event.condition, context,)
            ):
                new_ctx = self.env["crapo.workflow.context"].create(
                    {
                        "workflow_id": rec_event.trigger_id.workflow_id.id,
                        "context_event_ids": [
                            (0, False, {"event_id": rec_event.id})
                        ],
                    }
                )
                new_ctx.set_context_entry(
                    rec_event.trigger_id.init_record_key, record
                )
                # Automatically set initial envent to done
                done_ctx_event = done_ctx_event | new_ctx.context_event_ids[0]

            else:

                # If event has event_context and record_id are matching and
                # condition is met the event_context are set to done
                for rec_ctx_event in rec_event.context_event_ids:
                    context["wf_context"] = rec_ctx_event.wf_context_id

                    if (
                        not rec_event.record_id_context_key
                        or rec_ctx_event.get_record_id() == record.id
                    ) and (
                        not rec_event.condition
                        or safe_eval(rec_event.condition, context,)
                    ):
                        done_ctx_event = done_ctx_event | rec_ctx_event

        if done_ctx_event:
            done_ctx_event.write({"done": True})
