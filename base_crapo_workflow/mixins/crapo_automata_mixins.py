# -*- coding: utf-8 -*-
# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api
from odoo import SUPERUSER_ID

import logging

class ObjectWithStateMixin(object):
    """
    Mixin class that can be used to define an Odoo Model eligible to be managed by a Crapo Automaton

    Should be use as a mixin class in existing objects
    """
    my_model_ref = fields.Many2one(comodel_name='ir.model',
                                   string="My model",
                                   help="A reference to current object's Model, used to help retrieve dynamic states",
                                   default=lambda self: self._get_my_model_ref(),
                                   compute="_get_my_model_ref",
                                   store=True, index=True, required=True)

    automaton = fields.Many2one(comodel_name='crapo.automaton',
                                string=u'Related automaton',
                                help="""The automaton describes the various transition an object can go through between states""",
                                compute='_get_model_automaton',
                                store=True, index=True, required=False)

    state = fields.Many2one(comodel_name='crapo.state',
                            string='State',
                            help="""State in which this object is""",
                            track_visibility='onchange',
                            domain=lambda self: self._get_state_domain(),
                            group_expand='_read_group_states',
                            default=lambda self: self._get_default_state(), 
                            store=True, index=True, required=True)

    # Reference to My Model:
    @api.model
    def _get_my_model_ref(self):
        my_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        for record in self:
            record.my_model_ref = my_model
        return my_model
    
    # Computes automaton for current model
    @api.depends('my_model_ref')
    def _get_model_automaton(self):
        logging.error("DEFAULT AUTOMATON %s => %s ",str(self),str(self.env.context))
        default_value = 0
        automaton_model = self.env['crapo.automaton']
        
        logging.error("RESEARCHING DEFAULT AUTOMATON %s => %s ",str(self),str(self.env.context))
        my_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        my_automaton = automaton_model.search([('model_id','=',my_model.id)], limit=1)
        if my_automaton:
            return my_automaton
        else:            
            logging.error("CREATING DEFAULT AUTOMATON %s => %s  ",str(self),str(my_model.name))
            return automaton_model.create({'name': 'Automaton for {}'.format(self._name),
                                                'model_id': my_model.id})

    # State Management
    def _get_state_domain(self, domain=None):
        result = []

        if self.automaton:
            result.append(('automaton', '=', self.automaton.id))

        return result

    def _get_default_state(self):
        domain = self._get_state_domain()
        state_model = self.env['crapo.state']

        logging.error("DEFAULT STATE %s => %s (%s, %s)",str(self),str(self._name),str(domain),str(self.automaton))

        automaton = self._get_model_automaton()

        if automaton:
            domain.append('|')
            domain.append(('is_start_state', '=', True))
            domain.append(('default_state', '=', 1))

        default_state =  state_model.search(domain, limit=1)

        if default_state:
            return default_state
        elif automaton:
            return state_model.create({'name':"New",'automaton':automaton.id})
        else:
            return False

    def _next_states(self):
        self.ensure_one()
        domain = self._get_state_domain()
        next_states = False
        if self.automaton:
            eligible_transitions = self.env['crapo.transition'].search(
                [('automaton', '=', self.automaton.id), ('from_state', '=', self.state.id)])
            target_ids = eligible_transitions.mapped(lambda x: x.to_state.id)

            if target_ids:
                domain.append(('id', 'in', target_ids))

                next_states = self.env['crapo.state'].search(domain)

        else:
            domain.append(('sequence', '>', self.state.sequence))
            next_states = self.env['crapo.state'].search(domain, limit=1)

        return next_states

    def _read_group_states(self, states, domain, order):
        search_domain = self._get_state_domain(domain=domain)
        state_ids = states._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return states.browse(state_ids)


class StateObjectMixin(object):
    """
    Mixin class that can be used to define a state object that can be used as a crapo_state

    Should be use as a mixin class in existing objects
    """

    automaton = fields.Many2one(string="Automaton",
                                comodel_name='crapo.automaton',
                                default=lambda self: self._get_default_automaton(),
                                store=True, required=True, index=True)

    default_state = fields.Boolean(string='Default state',
                                   help='Might be use as default stage.', default=False, 
                                   store=True)

    # Transitions (inverse relations)

    transitions_to = fields.One2many(string='Incomint transitions',
                                     comodel_name='crapo.transition',
                                     inverse_name='to_state')

    transitions_from = fields.One2many(string='Outgoing transitions',
                                       comodel_name='crapo.transition',
                                       inverse_name='from_state'
                                       )
    # computed field to identify start and end states

    is_start_state = fields.Boolean("Start State", compute="_is_start_state", store=True, index=True)

    is_end_state = fields.Boolean("End State", compute="_is_end_state", store=True, index=True)

    @api.depends('transitions_to', 'automaton')
    def _is_start_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_start_state = True
            else:
                record.is_start_state = False

    @api.depends('transitions_from', 'automaton')
    def _is_end_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_end_state = True
            else:
                record.is_end_state = False

    def _do_search_default_automaton(self):
        logging.error("PATA PROUT SEARCH DE StateObjectMixin")
        return False

    @api.model
    def _get_default_automaton(self):
        logging.error("PATA PROUT DE StateObjectMixin")
        default_value = 0
        if 'current_automaton' in self.env.context:
            try:
                default_value = int(self.env.context.get('current_automaton'))
            except:
                default_value = 0
        else:
            return self._do_search_default_automaton()

        return self.env['crapo.automaton'].browse(default_value)

class WrappedStateMixin(object):
    """
    Mixin class that can be used to define a state object that wraps an existing model object
    but can be used as a crapo_state

    Should be use as a mixin class in existing objects
    """

    _inherits = {'crapo.state':'crapo_state'}

    crapo_state = fields.Many2one(comodel_name='crapo.state',
                                  string='Related Crapo State',
                                  store=True, index=True, required=True,
                                  ondelete='cascade')

    automaton = fields.Many2one(string="Automaton",
                                comodel_name='crapo.automaton',
                                default=lambda self: self._get_default_automaton(),
                                store=True, required=True, index=True)

    default_state = fields.Boolean(string='Default state',
                                   help='Might be use as default stage.', default=False, 
                                   store=True)

    # Transitions (inverse relations)

    transitions_to = fields.One2many(string='Incomint transitions',
                                     comodel_name='crapo.transition',
                                     inverse_name='to_state')

    transitions_from = fields.One2many(string='Outgoing transitions',
                                       comodel_name='crapo.transition',
                                       inverse_name='from_state'
                                       )
    # computed field to identify start and end states

    is_start_state = fields.Boolean("Start State", compute="_is_start_state", store=True, index=True)

    is_end_state = fields.Boolean("End State", compute="_is_end_state", store=True, index=True)

    @api.depends('transitions_to', 'automaton')
    def _is_start_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_start_state = True
            else:
                record.is_start_state = False

    @api.depends('transitions_from', 'automaton')
    def _is_end_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_end_state = True
            else:
                record.is_end_state = False

    @api.model
    def _get_default_automaton(self):
        logging.error("PATA PROUT DE WrappedStateMixin")
        default_value = 0
        if 'current_automaton' in self.env.context:
            try:
                default_value = int(self.env.context.get('current_automaton'))
            except:
                default_value = 0
        else:
            return self._do_search_default_automaton()

        return self.env['crapo.automaton'].browse(default_value)

    def _do_search_default_automaton(self):
        logging.error("PATA PROUT SEARCH DE WrappedStateMixin")
        automaton_model = self.env['crapo.automaton']
        my_model = self.env['ir.model'].search([('model', '=', self._state_for_model)], limit=1)
        my_automaton = automaton_model.search([('model_id', '=', my_model.id)])
        if not my_automaton:
            my_automaton = automaton_model.create({'name': 'Automaton for {}'.format(self._state_for_model),
                                                    'model_id': my_model.id})
        return my_automaton

    def _compute_related_state(self,values={}):
        my_automaton = self._do_search_default_automaton()

        logging.error("GAABLLUUU  WrappedStateMixin %s =>  (%s)",str(self),str(self.crapo_state))

        if not self.crapo_state:
            if not my_automaton:
                logging.error("NO DEFAULT AUTOMATON FOR  WrappedStateMixin %s => %s (%s)",str(self),str(self._state_for_model),str(my_automaton))
                return False
            else:
                if not 'name' in values:
                    values['name'] ='Default State for %s'%self.id
                values['automaton'] = my_automaton.id        
                return self.env['crapo.state'].create(values)
                