# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class WorkflowStateMachine(models.Model):
    """
    A state-machine (automaton) describes and automates the various transitions between states of a given business object class

    There can be a single state machine per Odoo Model Object

    """
    _name = 'crapo.automaton'
    _description = 'An automaton is a state machine for a given Odoo Model'
    _order = 'name,model_id'
    _record_name = 'name'

    _sql_constraints = [
        ('unique_per_model_id',
         'unique(model_id)',
         'Choose another value - automaton has to be unique per Model !')
    ]

    name = fields.Char(string=_(u'Name'),
                       help=_(u"State's name"), required=True, translate=True)

    model_id = fields.Many2one(string=_(u'Model'), help=_(u"Business Model for which this state is relevant"),
                               comodel_name="ir.model",
                               )

    start_state = fields.Many2one(string=_(u'Start State'),
                                  comodel_name='crapo.state')

    end_state = fields.Many2one(string=_(u'End State'),
                                comodel_name='crapo.state')

    transitions = fields.One2many(string=(u'Transitions'),
                                  comodel_name='crapo.transition',
                                  inverse_name='automaton',
                                  domain=lambda self: self._get_statetransition_domain())

    states = fields.One2many(string=(u'States'),
                             comodel_name='crapo.state',
                             inverse_name='automaton',
                             domain=lambda self: self._get_statetransition_domain())

    # State Management
    def _get_statetransition_domain(self):
        if self.model_id:
            return [('model_id', '=', self.model_id.id)]
        else:
            return []

    @api.onchange('model_id')
    def _reset_domains_and_contents(self):
        # TODO
        return
