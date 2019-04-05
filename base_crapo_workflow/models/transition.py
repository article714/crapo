# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models, _, api, exceptions


class StateMachineTransition(models.Model):
    """
    A transition between two states
    """
    _name = 'crapo.transition'
    _description = 'Transition between two states'

    name = fields.Char(string=_(u'Name'),
                       help=_(u"Transition's name"), required=True, translate=True, size=32)

    description = fields.Text(string=_(u'Description'),
                              required=False, translate=True, size=256)

    automaton = fields.Many2one(string="Automaton",
                                comodel_name='crapo.automaton',
                                default=lambda self: self._get_default_automaton(),
                                store=True, required=True, index=True)

    model_id = fields.Many2one(string=_(u'Model'),
                               comodel_name="ir.model",
                               related='automaton.model_id'
                               )

    from_state = fields.Many2one(string='From state',
                                 comodel_name='crapo.state',
                                 ondelete='cascade', required=True, index=True)

    to_state = fields.Many2one(string='To state',
                               comodel_name='crapo.state',
                               ondelete='cascade', required=True, index=True)

    preconditions = fields.Char(string=_(u"Pre-conditions"), help=_(u"""Conditions to be checked before initiating this transition.
    
Evaluation environment contains 'object' which is a reference to the object to be checked, and 'env' which is a reference to odoo environment"""),
                                required=False)

    postconditions = fields.Char(string=_(u"Post-conditions"), help=_(u"""Conditions to be checked before ending this transition.

Evaluation environment contains 'object' which is a reference to the object to be checked, and 'env' which is a reference to odoo environment
    """),
                                 required=False)

    action = fields.Many2one(string=_(u'Action to be executed when transitioning'),
                             comodel_name='crapo.action',  required=False)

    async_action = fields.Boolean(string=_(u"Async action"),
                                  help=_(u"Action will be run asynchronously, after transition is completed"),
                                  default=False
                                  )

    write_before = fields.Boolean(string=_(u"Write Object before"),
                                  help=_(u"""All updates to object will be commited before transitioning

This is useful for transitions where preconditions needs to be tested with values that might have either changed together with the state change
or during the write process (computed fields) """),
                                  default=False
                                  )

    @api.onchange('model_id')
    def _changed_model(self):
        self.action = False
        self.from_state = False
        self.to_state = False

    def _get_default_automaton(self):
        default_value = 0
        if 'current_automaton' in self.env.context:
            try:
                default_value = int(self.env.context.get('current_automaton'))
            except:
                default_value = 0
                
        return self.env['crapo.automaton'].browse(default_value)
                
