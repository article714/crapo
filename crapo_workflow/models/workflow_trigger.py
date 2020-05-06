"""
see README for details
"""
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.queue_job.job import job


class WorkflowTrigger(models.Model):
    """
        A trigger is the logical brick between activities. It will trigger all
        of its activities when triggered.

        - Initial trigger:  this is the first trigger of the workflow it will
          initiate a crapo.workflow.context when triggered

        - End trigger: this is the last trigger of the workflow it will distroy
          the crapo.workflow.context that triggered it
    """

    _name = "crapo.workflow.trigger"

    name = fields.Char(required=True)

    workflow_id = fields.Many2one("crapo.workflow")

    trigger_type = fields.Selection(
        [
            ("init", "Initiale trigger"),
            ("end", "End trigger"),
            ("joiner", "Joiner trigger between activities"),
        ],
        required=True,
        default="joiner",
    )

    to_activity_ids = fields.Many2many(
        "crapo.workflow.activity",
        "crapo_workflow_tj_trigger_activity",
        domain="[('workflow_id', '=', workflow_id)]",
    )
    from_activity_ids = fields.Many2many(
        "crapo.workflow.activity",
        "crapo_workflow_tj_activity_trigger",
        domain="[('workflow_id', '=', workflow_id)]",
    )

    event_ids = fields.One2many("crapo.workflow.event", "trigger_id")

    event_logical_condition = fields.Char(
        help="If empty, all event must be done to trigger the trigger"
    )

    init_record_key = fields.Char()

    @job
    @api.multi
    def check_and_run(self, wf_context_id):
        """
            Evaluate event_logical_condition in the context passer in parameter
            to see if trigger is triggered. If so run activities or destroy wf
            context in case of end trigger type.
        """
        for rec in self:
            context_event_ids = wf_context_id.context_event_ids.filtered(
                lambda context_event: context_event.trigger_id == rec
            )
            # Evaluate event_logical_condition if there is one
            if rec.event_logical_condition:
                context = {"wf": wf_context_id}
                for context_event in context_event_ids:
                    context[context_event.event_id.name] = context_event.done

                run = safe_eval(rec.event_logical_condition, context)
            # Else we considerate that all event must be done
            else:
                run = all(context_event_ids.mapped("done"))

            if run:
                # Destroy context
                if rec.trigger_type == "end":
                    wf_context_id.unlink()

                # Run activities
                else:
                    for activity_id in rec.to_activity_ids:
                        rec.run_activity(activity_id, wf_context_id)

    def run_activity(self, activity_id, wf_context_id):
        """
            Run activity passed in parameter with the context passed in
            parameter
        """
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
        """
            Automaticaly add or remove activity_ended event based on
            from activity_ids field
        """
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
                        "model_id": self.env[
                            "ir.model"
                        ]._get_id(  # pylint: disable=protected-access
                            activity_id._name  # pylint: disable=protected-access
                        ),
                        "condition": "activity_wf_ctx_id == wf_context",
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
        """
            Validate that all event are used in the condition
        """
        for rec in self:
            if rec.event_logical_condition:
                context = {}
                # Check if all event are found in event_logical_condition
                for event in rec.event_ids:
                    event_name = event.name
                    context[event_name] = False
                    # Regexp to extract all word (and so all variable) from
                    # event_logical_condition
                    variables = re.findall(r"\w+", rec.event_logical_condition)
                    if event_name not in variables:
                        raise ValidationError(
                            _("Event ({}) is not used in {}").format(
                                event_name,
                                self._fields["event_logical_condition"].string,
                            )
                        )
                # Check syntax
                safe_eval(rec.event_logical_condition, context)

    def check_init_trigger(self):
        """
            Test if an init trigger has at most 1 trigger event
        """
        for rec in self:
            if rec.trigger_type == "init" and len(rec.event_ids) > 1:
                raise ValidationError(
                    _("Init trigger can have only one trigger event")
                )

    # ==========================
    # Write / Create
    # ==========================

    @api.model
    def create(self, values):
        """
        Override default creation method
        """
        rec = super(WorkflowTrigger, self).create(values)
        if values.get("event_logical_condition"):
            rec.check_event_logical_condition()

        rec.check_init_trigger()

        return rec

    @api.multi
    def write(self, values):
        """
        Check conditions before writing record
        """
        res = super(WorkflowTrigger, self).write(values)
        if values.get("event_logical_condition"):
            self.check_event_logical_condition()

        self.check_init_trigger()

        return res
