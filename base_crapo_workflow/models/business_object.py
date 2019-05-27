# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, _, exceptions, api
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base_crapo_workflow.mixins import (
    crapo_automata_mixins,
)  # pylint: disable=odoo-addons-relative-import


class CrapoBusinessObject(
    crapo_automata_mixins.ObjectWithStateMixin, models.Model
):
    """
    Base class to define a Business Object.

    Should be use as a mixin class in existing objects
    """

    _name = "crapo.business.object"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = """
    An object on which to  in a workflow, specific to a given model
    """
    _sync_state_field = ""

    @api.multi
    def write(self, values):
        """
        we override write method in order to preventing transitioning
        to a non eligible state
        """
        # Look for a change of state
        target_state_id = None
        result = True

        if "state" in values:
            target_state_id = values["state"]

        # check if there is a change state needed
        if target_state_id is not None:

            # Check if next state is valid
            for record in self:
                if record.state and target_state_id:
                    next_states = record._next_states()
                    if not next_states:
                        raise exceptions.ValidationError(
                            _(
                                u"""No target state is elegible
                             for transitionning"""
                            )
                        )
                    if target_state_id not in next_states.ids:
                        raise exceptions.ValidationError(
                            _(u"State is not in eligible target states")
                        )

            # Search for elected transition
            transition_elected = self.env["crapo.transition"].search(
                [
                    ("from_state", "=", self.state.id),
                    ("to_state", "=", target_state_id),
                ],
                limit=1,
            )

            if transition_elected:
                is_valid = True
                result = True

                if transition_elected.write_before:
                    result = super(CrapoBusinessObject, self).write(values)

                # Test preconditions
                if transition_elected.preconditions:
                    for obj in self:
                        try:
                            is_valid = safe_eval(
                                transition_elected.preconditions,
                                {"object": obj, "env": self.env},
                            )

                        except Exception as e:
                            logging.error(
                                (
                                    "CRAPO: Failed to validate "
                                    "transition preconditions: %s"
                                ),
                                str(e),
                            )
                            is_valid = False

                        # Raise an error if not valid
                        if not is_valid:
                            raise exceptions.ValidationError(
                                _("Invalid Pre-conditions for Object: %s")
                                % obj.display_name
                            )

                # Should we go for it?
                if is_valid and transition_elected.action:
                    # does action needs to be taken asynchronously?
                    action = self.env["crapo.action"].browse(
                        transition_elected.action.id
                    )
                    context = {
                        "active_model": self._name,
                        "active_id": self.id,
                        "active_ids": self.ids,
                    }
                    if action:
                        if transition_elected.async_action:
                            action.with_delay().run_async(context)
                        else:
                            action.with_context(context).run()

                # Test postconditions if action is not asynchronous
                if (
                    transition_elected.postconditions
                    and not transition_elected.async_action
                ):
                    for obj in self:
                        try:
                            is_valid = safe_eval(
                                transition_elected.postconditions,
                                {"object": obj, "env": self.env},
                            )
                        except Exception as e:
                            logging.error(
                                (
                                    "CRAPO: Failed to validate transition "
                                    "postconditions: %s"
                                ),
                                str(e),
                            )
                            is_valid = False
                        # Raise an error if not valid
                        if not is_valid:
                            raise exceptions.ValidationError(
                                _(u"Invalid Post-conditions for Object: %s")
                                % obj.display_name
                            )
                # writing after id needed
                if not transition_elected.write_before:
                    result = super(CrapoBusinessObject, self).write(values)

                return result

        else:
            return super(CrapoBusinessObject, self).write(values)
