# coding: utf-8

"""
©2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, api
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins

import logging


class CrmStageWithMixin(crapo_automata_mixins.WrappedStateMixin, models.Model):
    _inherit = "crm.stage"
    _state_for_model = "crm.lead"

    def write(self, values):
        if len(self) == 1:
            if 'crapo_state' not in values and not self.crapo_state:
                if 'name' in values:
                    vals = {'name': values['name']}
                else:
                    vals = {'name': self.name}
                mystate = self._compute_related_state(vals)
                values['crapo_state'] = mystate.id

        return super(CrmStageWithMixin, self).write(values)

    @api.model
    def create(self, values):
        if 'crapo_state' not in values and not self.crapo_state:
            if 'name' in values:
                vals = {'name': values['name']}
            mystate = self._compute_related_state(vals)
            values['crapo_state'] = mystate.id

        return super(CrmStageWithMixin, self).create(values)

    @api.model_cr_context
    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.
            Overridden here because we need to wrap existing stages in
            a new crapo_state for each stage (including a default automaton)
        """
        if column_name not in ["crapo_state"]:
            super(CrmStageWithMixin, self)._init_column(column_name)
        else:
            default_compute = self._compute_related_state

            query = 'SELECT id, name FROM "%s" WHERE "%s" is NULL' % (
                self._table, column_name)
            self.env.cr.execute(query)
            stages = self.env.cr.fetchall()

            for stage in stages:
                default_value = default_compute(
                    self, values={'name': stage[1]})

                query = 'UPDATE "%s" SET "%s"=%%s WHERE id = %s' % (
                    self._table, column_name, stage[0])
                logging.error("TADAAA: %s" % query)
                self.env.cr.execute(query, (default_value,))
