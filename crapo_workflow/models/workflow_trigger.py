# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job
from odoo.tools.safe_eval import safe_eval


class WorkflowTrigger(models.Model):
    """
        A trigger step in a Workflow
    """

    _name = "crapo.workflow.trigger"

    name = fields.Char()

    workflow_id = fields.Many2one("crapo.workflow")

    to_activity_ids = fields.Many2many(
        "crapo.workflow.activity", "crapo_workflow_tj_trigger_activity"
    )
    from_activity_ids = fields.Many2many(
        "crapo.workflow.activity", "crapo_workflow_tj_activity_trigger"
    )

    event_ids = fields.One2many("crapo.workflow.event", "trigger_id")

    event_logical_condition = fields.Char()

    init_trigger = fields.Boolean(default=False, required=True)

    end_trigger = fields.Boolean(default=False, required=True)

    init_record_key = fields.Char()

    @job
    def check_and_run(self, wf_context_id):
        for rec in self:
            context_event_ids = wf_context_id.context_event_ids.filtered(
                lambda context_event: context_event.trigger_id == rec
            )
            if rec.event_logical_condition:
                context = {"wf": wf_context_id}
                for context_event in context_event_ids:
                    context[context_event.event_id.name] = context_event.done

                run = safe_eval(rec.event_logical_condition, context)
            else:
                run = all(context_event_ids.mapped("done"))

            if run:
                if rec.end_trigger:
                    wf_context_id.unlink()
                else:
                    for activity_id in rec.to_activity_ids:
                        rec.start_activity(activity_id, wf_context_id)

    def start_activity(self, activity_id, wf_context_id):
        self.ensure_one()

        for rec in wf_context_id.context_event_ids.filtered(
            lambda rec: rec.trigger_id == self
        ):
            rec.unlink()

        for rec in self.search([("from_activity_ids", "=", activity_id.id)]):
            wf_context_id.write(
                {
                    "context_event_ids": [
                        (0, False, {"event_id": rec_event.id})
                        for rec_event in rec.event_ids
                    ]
                }
            )

        activity_id.with_delay().run(wf_context_id)

    @api.onchange("from_activity_ids")
    def activity_ended_event_consistency(self):
        self.ensure_one()
        values = []

        event_activity_ended_ids = self.event_ids.filtered(
            lambda evt: evt.event_type == "activity_ended"
        )

        # Add missing acitivy_ended event
        for activity_id in (
            self.from_activity_ids
            - event_activity_ended_ids.mapped("activity_id")
        ):
            values.append(
                (
                    0,
                    0,
                    {
                        "event_type": "activity_ended",
                        "activity_id": activity_id.id,
                        "model_id": self.env["ir.model"]._get_id(
                            activity_id._name
                        ),
                    },
                )
            )

        # Remove extra activity_ended event
        for event_id in event_activity_ended_ids.filtered(
            lambda evt: evt.activity_id not in self.from_activity_ids
        ):
            values.append((2, event_id.id, 0))

        if values:
            self.update({"event_ids": values})

    def check_event_logical_condition(self):
        for rec in self:
            if rec.event_logical_condition:
                context = {}
                for event in rec.event_ids:
                    event_name = event.name
                    context[event_name] = False
                    if not event_name in rec.event_logical_condition:
                        raise ValidationError(
                            _("Event ({}) is not used in {}").format(
                                event_name,
                                self._fields["event_logical_condition"].string,
                            )
                        )
                safe_eval(rec.event_logical_condition, context)

    def check_init_trigger(self):
        """
            Test if an init trigger has at most 1 trigger event
        """
        for rec in self:
            if rec.init_trigger and len(rec.event_ids) > 1:
                raise ValidationError(
                    _("Init trigger can have only one trigger event")
                )

    @api.model
    def create(self, values):
        rec = super(WorkflowTrigger, self).create(values)
        if values.get("event_logical_condition"):
            rec.check_event_logical_condition()

        rec.check_init_trigger()

        return rec

    @api.multi
    def write(self, values):
        res = super(WorkflowTrigger, self).write(values)
        if values.get("event_logical_condition"):
            self.check_event_logical_condition()

        self.check_init_trigger()

        return res
