"""
©2019-2020
License: AGPL-3

@author: D. Couppé (Article 714)

"""
import logging
from odoo.addons.component.core import Component

from odoo import api


class TransitionListener(Component):
    _name = "crapo.transition.event.listener"
    _inherit = "base.event.listener"

    @api.multi
    def on_transition(self, record, from_state, to_state):
        logging.info(
            "OOOOOOOOOOOOOOOO !!!!! %s, %s, %s, %s",
            self,
            record,
            from_state,
            to_state,
        )
