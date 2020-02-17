# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, api, exceptions, _
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from .crapo_readonly_view_mixin import ReadonlyViewMixin


class ObjectWithStateMixin(ReadonlyViewMixin):



class StateObjectMixin(object):



class WrappedStateMixin(StateObjectMixin):
    """
    Mixin class that can be used to define a state object that
    wraps an existing model defining a state for another model

    The wrapped object can be used as a crapo_automaton_state

    Should be use as a mixin class in existing objects
    """

    _inherits = {"crapo.automaton.state": "crapo_automaton_state"}

    crapo_automaton_state = fields.Many2one(
        comodel_name="crapo.automaton.state",
        string="Related Crapo State",
        store=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    def _do_search_default_automaton(self):
        """
        finds or creates the default automaton (one per model)
        """
        automaton_model = self.env["crapo.automaton"]
        my_model = self.env["ir.model"].search(
            [("model", "=", self._state_for_model)], limit=1
        )
        my_automaton = automaton_model.search([("model_id", "=", my_model.id)])
        if not my_automaton:
            my_automaton = automaton_model.create(
                {
                    "name": "Automaton for {}".format(self._state_for_model),
                    "model_id": my_model.id,
                }
            )
        return my_automaton

    def _compute_related_state(
        self, values={}
    ):  # pylint: disable=dangerous-default-value
        """
        Create a new crapo_automaton_state for an existing record of the WrappedState
        """
        my_automaton = self._do_search_default_automaton()

        if not self.crapo_automaton_state:
            if not my_automaton:
                return False
            else:
                if "name" not in values:
                    values["name"] = "Default State for %s" % self.id
                values["automaton_id"] = my_automaton.id
                return self.env["crapo.automaton.state"].create(values)
