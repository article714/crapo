"""
See README for details
"""
from odoo.addons.component.core import Component
from odoo.addons.component_event.components.event import skip_if


class WorkflowListener(Component):
    """
    The part of Crapo that listens for events on records and put them in
    queues for later consumption by workflows
    """

    _name = "crapo.workflow.listener"
    _inherit = "base.event.listener"

    def wf_event(self, name, values):
        """
        Send a workflow event
        """
        try:
            mdl_broker = self.env["crapo.workflow.broker"]
        except KeyError:
            return

        mdl_broker.with_context({"notify_event": True}).with_delay().notify(
            name, values
        )

    @skip_if(
        lambda self, record, fields: self.env.context.get("notify_event")
        or record._module  # pylint: disable=protected-access
        in ("queue", "connector")
    )
    def on_record_create(self, record, fields):
        """
        Sends event when a record creation occurs
        """

        self.wf_event("record_create", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record, fields: self.env.context.get("notify_event")
        or record._module  # pylint: disable=protected-access
        in ("queue", "connector")
    )
    def on_record_write(self, record, fields):
        """
        Sends event when a write occurs on a record
        """
        self.wf_event("record_write", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record: self.env.context.get("notify_event")
        or record._module  # pylint: disable=protected-access
        in ("queue", "connector")
    )
    def on_record_unlink(self, record):
        """
        Sends event when a record deletion occurs
        """
        self.wf_event("record_unlink", {"record": record})
