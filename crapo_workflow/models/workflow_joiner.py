# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job
from odoo.tools.safe_eval import safe_eval


class WorkflowJoiner(models.Model):
    """
        A joiner step in a Workflow
    """

    _name = "crapo.workflow.joiner"

    workflow_id = fields.Many2one("crapo.workflow")

    to_activity_ids = fields.Many2many("crapo.workflow.activity")

    event_ids = fields.One2many("crapo.workflow.joiner.event", "joiner_id")

    event_logical_condition = fields.Char()

    @job
    def check_and_run(self, wf_context_id):
        for rec in self:
            event_status_ids = wf_context_id.context_event_status_ids.filtered(
                lambda event_status: event_status.joiner_id == rec.id
            )
            if rec.event_logical_condition:
                context = {}
                for event_status in event_status_ids:
                    context[
                        event_status.joiner_event_id.name
                    ] = event_status.done
                run = safe_eval(rec.event_logical_condition, context)
            else:
                run = all(event_status_ids).mapped("done")

            if run:
                for activity_id in rec.to_activity_ids:
                    activity_id.with_delay().run(wf_context_id)

    def check_event_logical_condition(self):
        for rec in self:
            if rec.event_logical_condition:
                context = {}
                for event in rec.event_ids:
                    event_name = event.name
                    context[event_name] = event.done
                    if not event_name in rec.event_logical_condition:
                        raise ValidationError(
                            _("Event ({}) is not used in {}").format(
                                event_name,
                                self._fields["event_logical_condition"].string,
                            )
                        )
                safe_eval(rec.event_logical_condition, context)

    @api.model
    def create(self, values):
        rec = super(WorkflowJoiner, self).create(values)
        if values.get("event_logical_condition"):
            rec.check_event_logical_condition()
        return rec

    @api.multi
    def write(self, values):
        res = super(WorkflowJoiner, self).write(values)
        if values.get("event_logical_condition"):
            self.check_event_logical_condition()
        return res


class WorkflowJoinerEvent(models.Model):

    _name = "crapo.workflow.joiner.event"

    _sql_constraints = [
        (
            "unique_name_per_joiner_id",
            "unique(name, joiner_id)",
            "Joiner event can't have the same name in the same joiner",
        )
    ]

    name = fields.Char()

    joiner_id = fields.Many2one("crapo.workflow.joiner")

    model_id = fields.Many2one("ir.model", required=True)

    context_joiner_event_status_ids = fields.One2many(
        "crapo.workflow.context.joiner.event.status", "joiner_event_id"
    )

    record_id_context_key = fields.Char()

    condition = fields.Char(
        help="""Conditions to be checked before set this event as done.""",
    )

    event_type = fields.Selection(
        [
            ("transition", "transition"),
            ("record_create", "record_create"),
            ("record_write", "record_write"),
            ("record_unlink", "record_unlink"),
            ("activity_ended", "activity_ended"),
        ]
    )

    transition_from_state = fields.Many2one("crapo.state")
    transition_to_state = fields.Many2one("crapo.state")

    @job
    @api.model
    def notify(self, event_type, values):

        domain = [("event_type", "=", event_type)]
        context = {"env": self.env, "values": values}
        if event_type == "transition":
            from_state = values["from_state"]
            to_state = values["to_state"]

            if from_state:
                domain.append(("transition_from_state", "=", from_state.id))

            domain.append(("transition_to_state", "=", to_state.id))

        else:
            record = values["record"]

            domain.append(
                ("model_id", "=", self.env["ir.model"]._get_id(record._name),)
            )

        logging.info("SEARCH DOMAIN : %s", domain)
        for rec_event in self.with_context(
            {"notify_joiner_event": True}
        ).search(domain):
            for rec_status in rec_event.context_joiner_event_status_ids:
                if (
                    not rec_event.record_id_context_key
                    or rec_status.record_id == record.id
                ) and (
                    not rec_event.condition
                    or safe_eval(rec_event.condition, context,)
                ):
                    rec_status.write({"done": True})

    # ================================
    # Write / Create
    # ================================

    @api.model
    def create(self, values):

        rec = super(WorkflowJoinerEvent, self).create(values)

        if not rec.name:
            rec.name = "_".join((rec.event_type, str(rec.id)))

        return rec
