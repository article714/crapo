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

    _sql_constraints = [
        (
            "unique_init_per_wf",
            "unique(init_joiner, workflow_id)",
            "Worklfow can have only one init joiner",
        )
    ]

    _name = "crapo.workflow.joiner"

    workflow_id = fields.Many2one("crapo.workflow")

    to_activity_ids = fields.Many2many(
        "crapo.workflow.activity", "crapo_workflow_tj_joiner_activity"
    )
    from_activity_ids = fields.Many2many(
        "crapo.workflow.activity", "crapo_workflow_tj_activity_joiner"
    )

    event_ids = fields.One2many("crapo.workflow.joiner.event", "joiner_id")

    event_logical_condition = fields.Char()

    init_joiner = fields.Boolean(default=False, required=True)

    end_joiner = fields.Boolean(default=False, required=True)

    init_record_key = fields.Char()

    @job
    def check_and_run(self, wf_context_id):
        for rec in self:
            event_status_ids = wf_context_id.context_event_status_ids.filtered(
                lambda event_status: event_status.joiner_id == rec
            )
            if rec.event_logical_condition:
                context = {"wf": wf_context_id}
                for event_status in event_status_ids:
                    context[
                        event_status.joiner_event_id.name
                    ] = event_status.done
                logging.info("YYYYYYYYYYYYYYYYYYYYYYY %s", context)
                run = safe_eval(rec.event_logical_condition, context)
            else:
                run = all(event_status_ids.mapped("done"))

            if run:
                if rec.end_joiner:
                    wf_context_id.unlink()
                else:
                    for activity_id in rec.to_activity_ids:
                        rec.start_activity(activity_id, wf_context_id)

    def start_activity(self, activity_id, wf_context_id):
        self.ensure_one()

        for rec in wf_context_id.context_event_status_ids.filtered(
            lambda rec: rec.joiner_id == self
        ):
            logging.info("AZERTRTYYYYY UNLINK %s", rec)
            rec.unlink()

        for rec in self.search([("from_activity_ids", "=", activity_id.id)]):
            logging.info("AZERTRTYYYYY ADD %s", rec)
            wf_context_id.write(
                {
                    "context_event_status_ids": [
                        (0, False, {"joiner_event_id": rec_event.id})
                        for rec_event in rec.event_ids
                    ]
                }
            )

        activity_id.with_delay().run(wf_context_id)

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

    def check_init_joiner(self):
        """
            Test if an init joiner has at most 1 joiner event
        """
        for rec in self:
            if rec.init_joiner and len(rec.event_ids) > 1:
                raise ValidationError(
                    _("Init joiner can have only one joiner event")
                )

    @api.model
    def create(self, values):
        rec = super(WorkflowJoiner, self).create(values)
        if values.get("event_logical_condition"):
            rec.check_event_logical_condition()

        rec.check_init_joiner()

        return rec

    @api.multi
    def write(self, values):
        res = super(WorkflowJoiner, self).write(values)
        if values.get("event_logical_condition"):
            self.check_event_logical_condition()

        self.check_init_joiner()

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

    activity_id = fields.Many2one("crapo.workflow.activity")

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
            logging.info("UUUUUUUUUUUUUUUUUUUUUUUUUUU")
            if rec_event.joiner_id.init_joiner:
                logging.info(
                    "GGGGGGGGGGGGGGGGGGGGGGGGGG %s, %s",
                    rec_event,
                    rec_event.joiner_id,
                )
                new_ctx = self.env["crapo.workflow.context"].create(
                    {
                        "workflow_id": rec_event.joiner_id.workflow_id.id,
                        "context_event_status_ids": [
                            (0, False, {"joiner_event_id": rec_event.id,},)
                        ],
                    }
                )
                new_ctx.set_context_entry(
                    rec_event.joiner_id.init_record_key, record
                )
                new_ctx.context_event_status_ids[0].write({"done": True})
            else:
                logging.info("OLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
                for rec_status in rec_event.context_joiner_event_status_ids:
                    context["wf"] = rec_status.wf_context_id
                    logging.info("ZAZZZZZZZZZZZZZZZZZZZZZZ")
                    if (
                        not rec_event.record_id_context_key
                        or rec_status.record_id == record.id
                    ) and (
                        not rec_event.condition
                        or safe_eval(rec_event.condition, context,)
                    ):
                        logging.info("VVVVVVVVVVVVVVVVVVVVVV \o/")
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
