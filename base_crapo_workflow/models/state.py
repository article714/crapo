# coding: utf-8

# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions

from odoo.addons.base_crapo_workflow.mixins import (
    crapo_automata_mixins,
)  # pylint: disable=odoo-addons-relative-import


class State(crapo_automata_mixins.StateObjectMixin, models.Model):
    """
    A state used in the context of an automaton
    """

    _name = "crapo.state"
    _description = u"State in a workflow, specific to a given model"
    _order = "sequence, name"

    name = fields.Char(help="State's name", required=True, translate=True, size=32)

    description = fields.Char(required=False, translate=True, size=256)

    sequence = fields.Integer(
        default=1, help="Sequence gives the order in which states are displayed"
    )

    fold = fields.Boolean(
        string="Folded in kanban",
        help=(
            "This stage is folded in the kanban view "
            "when there are no records in that stage to display."
        ),
        default=False,
    )

    @api.multi
    def write(self, values):
        """
        Override default method to check if there is a valid default_state
        """
        if "default_state" in values:
            if values["default_state"]:
                if len(self) > 1:
                    raise exceptions.ValidationError(
                        _(u"There should only one default state per model")
                    )
                else:
                    found = self.search(
                        [
                            ("default_state", "=", True),
                            ("automaton", "=", self.automaton.id),
                            ("id", "!=", self.id),
                        ]
                    )
                    for s in found:
                        s.write({"default_state": False})

        return super(State, self).write(values)
