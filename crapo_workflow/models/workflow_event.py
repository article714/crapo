# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api


class WorkflowEvent(models.Model):
    """
        Event definition
    """

    _name = "crapo.workflow.event"

    _sql_constraints = [
        (
            "unique_name_per_trigger_id",
            "unique(name, trigger_id)",
            "Trigger event can't have the same name in the same trigger",
        )
    ]

    name = fields.Char()

    trigger_id = fields.Many2one("crapo.workflow.trigger")

    model_id = fields.Many2one("ir.model", required=True)

    context_event_ids = fields.One2many(
        "crapo.workflow.context.event", "event_id"
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

    # ================================
    # Write / Create
    # ================================

    @api.model
    def create(self, values):
        """
            Automaticaly add a default name if not defined
        """
        rec = super(WorkflowEvent, self).create(values)

        if not rec.name:
            rec.name = "_".join((rec.event_type, str(rec.id)))

        return rec
