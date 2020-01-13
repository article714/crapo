# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api
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

    def check_and_run(self):
        if all(self.event_ids.mapped("done")):
            for activity_id in self.to_activity_ids:
                activity_id.with_delay().run_async()


class WorkflowJoinerEvent(models.Model):

    _name = "crapo.workflow.joiner.event"

    joiner_id = fields.Many2one("crapo.workflow.joiner")

    done = fields.Boolean(default=False, required=True)

    model_id = fields.Many2one("ir.model", required=True)

    record_id = fields.Integer()

    condition = fields.Char(
        help="""Conditions to be checked before set this event as done.""",
    )

    event_type = fields.Selection(
        [
            ("transition", "transition"),
            ("record_create", "record_create"),
            ("record_write", "record_write"),
            ("record_unlink", "record_unlink"),
        ]
    )

    transition_from_state = fields.Many2one("crapo.state")
    transition_to_state = fields.Many2one("crapo.state")

    @job
    @api.model
    def notify(self, event_type, values):

        domain = [("event_type", "=", event_type), ("done", "=", False)]
        if event_type == "transition":
            from_state = values["from_state"]
            to_state = values["to_state"]

            if from_state:
                domain.append(("transition_from_state", "=", from_state.id))

            domain.append(("transition_to_state", "=", to_state.id))

        else:
            record = values["record"]
            logging.info(
                "PPPPPPPPPPPPPPPPP %s",
                self.env.ref(
                    "{}.model_{}".format(
                        record._module, record._name.replace(".", "_")
                    )
                ),
            )
            domain.append(
                (
                    "model_id",
                    "=",
                    self.env.ref(
                        "{}.model_{}".format(
                            record._module, record._name.replace(".", "_")
                        )
                    ).id,
                )
            )

            if event_type in ("record_write", "record_unlink"):
                domain.append(("record_id", "=", record.id))

        logging.info("SAERCH DOMAIN : %s", domain)
        self.search(domain).filtered(
            lambda rec: not rec.condition
            or safe_eval(rec.condition, {"object": rec, "env": self.env},)
        ).write({"done": True})

    @api.multi
    def write(self, values):
        res = super(WorkflowJoinerEvent, self).write(values)

        if values.get("done"):
            self.mapped("joiner_id").check_and_run()

        return res
