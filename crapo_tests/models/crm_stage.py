"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""

import logging

from odoo import models, api
from psycopg2.sql import Identifier
from odoo.addons.base_crapo_workflow.mixins import (
    crapo_automata_mixins,
)  # pylint: disable=odoo-addons-relative-import


class CrmStageWithMixin(crapo_automata_mixins.WrappedStateMixin, models.Model):
    _inherit = "crm.stage"
    _state_for_model = "crm.lead"

    def write(self, values):
        if len(self) == 1:
            if "crapo_state" not in values and not self.crapo_state:
                if "name" in values:
                    vals = {"name": values["name"]}
                else:
                    vals = {"name": self.name}
                mystate = self._compute_related_state(vals)
                values["crapo_state"] = mystate.id

        return super(CrmStageWithMixin, self).write(values)

    @api.model
    def create(self, values):
        """ Create a new crapo_stage for each crm_stage
        """
        if "crapo_state" not in values and not self.crapo_state:
            if "name" in values:
                vals = {"name": values["name"]}
            mystate = self._compute_related_state(vals)
            values["crapo_state"] = mystate.id

        return super(CrmStageWithMixin, self).create(values)

    @api.model_cr_context
    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.
            Overridden here because we need to wrap existing stages in
            a new crapo_state for each stage (including a default automaton)
        """
        if column_name not in ["crapo_state"]:
            return super(CrmStageWithMixin, self)._init_column(column_name)
        else:
            default_compute = self._compute_related_state

            tname = Identifier(self._table).as_string(
                self.env.cr._obj  # pylint: disable=protected-access
            )
            cname = Identifier(column_name).as_string(
                self.env.cr._obj  # pylint: disable=protected-access
            )

            logging.error(
                "MMMMMAIS %s (%s) -> %s", tname, type(tname), str(tname)
            )

            self.env.cr.execute(
                "SELECT id, name FROM %s WHERE %s is NULL", (tname, cname)
            )
            stages = self.env.cr.fetchall()

            for stage in stages:
                default_value = default_compute(values={"name": stage[1]})
                self.env.cr.execute(
                    "UPDATE %s SET %s=%s WHERE id = %s",
                    (tname, cname, default_value.id, stage[0]),
                )
        return True
