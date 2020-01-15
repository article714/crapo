"""
©2019-2020
License: AGPL-3

@author: D. Couppé (Article 714)

"""
import logging
from odoo.addons.component.core import Component
from odoo.addons.component_event.components.event import skip_if

from odoo import api


class WorkflowListener(Component):
    _name = "crapo.workflow.listener"
    _inherit = "base.event.listener"

    def on_transition(self, record, from_state, to_state):
        logging.info(
            "OOOOOOOO on_transition OOOOOOOO !!!!! %s, %s, %s, %s",
            self,
            record,
            from_state,
            to_state._module,
        )
        self.env["crapo.workflow.joiner.event"].with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify(
            "transition",
            {
                "record": record,
                "from_state": from_state,
                "to_state": to_state,
            },
        )

    def on_activity_ended(self, record):
        logging.info(
            "OOOOOOOO on_activity_ended OOOOOOOO !!!!! %s, %s", self, record
        )
        self.env["crapo.workflow.joiner.event"].with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify("activity_ended", {"record": record})

    @skip_if(
        lambda self, record, fields: self.env.context.get(
            "notify_joiner_event"
        )
        or record._module in ("queue", "connector")
    )
    def on_record_create(self, record, fields):
        logging.info(
            "OOOOOOOO on_record_create OOOOOOOO !!!!! %s, %s, %s",
            self,
            record._module,
            fields,
        )
        self.env["crapo.workflow.joiner.event"].with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify(
            "record_create", {"record": record, "fields": fields}
        )

    @skip_if(
        lambda self, record, fields: self.env.context.get(
            "notify_joiner_event"
        )
        or record._module in ("queue", "connector")
    )
    def on_record_write(self, record, fields):
        logging.info(
            "OOOOOOOO on_record_write OOOOOOOO !!!!! %s, %s, %s",
            self,
            record._module,
            fields,
        )
        self.env["crapo.workflow.joiner.event"].with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify(
            "record_write", {"record": record, "fields": fields}
        )

    @skip_if(
        lambda self, record: self.env.context.get("notify_joiner_event")
        or record._module in ("queue", "connector")
    )
    def on_record_unlink(self, record):
        logging.info(
            "OOOOOOOO on_record_unlink OOOOOOOO !!!!! %s, %s", self, record
        )
        self.env["crapo.workflow.joiner.event"].with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify("record_unlink", {"record": record})
