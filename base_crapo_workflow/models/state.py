# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions


class State(models.Model):
    """
    A state used in the context of an automaton
    """
    _name = 'crapo.state'
    _description = u"State in a workflow, specific to a given model"
    _order = "model_id,sequence, name, id"

    name = fields.Char(string=_(u'Name'),
                       help=_(u"State's name"), required=True, translate=True, size=32)

    description = fields.Char(string=_(u'Description'),
                              required=False, translate=True, size=256)

    automaton = fields.Many2one(string="Automaton",
                                comodel_name='crapo.automaton',
                                default=lambda self: self._get_default_automaton(),
                                store=True, required=True, index=True)

    model_id = fields.Many2one(string=_(u'Model'), help=_(u"Business Model for which this state is relevant"),
                               comodel_name="ir.model",
                               related='automaton.model_id'
                               )

    sequence = fields.Integer(string=_(u'Sequence'), default=1, help=_(
        u"Sequence gives the order in which states are displayed"))

    default_state = fields.Boolean(string=_(u'Default state'),
                                   help=_(u'Might be use as default stage.'), default=False, store=True)

    fold = fields.Boolean(string=_(u'Folded in kanban'),
                          help=_(u'This stage is folded in the kanban view when there are no records in that stage to display.'), default=False)

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

    @api.depends('transitions_to', 'automaton', 'model_id')
    def _is_start_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_start_state = True
            else:
                record.is_start_state = False

    @api.depends('transitions_from', 'automaton', 'model_id')
    def _is_end_state(self):
        for record in self:
            if len(record.transitions_to) == 0 or record.transitions_to == False:
                record.is_end_state = True
            else:
                record.is_end_state = False

    def _get_default_automaton(self):
        default_value = 0
        if 'current_automaton' in self.env.context:
            try:
                default_value = int(self.env.context.get('current_automaton'))
            except:
                default_value = 0

        return self.env['crapo.automaton'].browse(default_value)

    def write(self, values):

        if "default_state" in values:
            if values["default_state"]:
                if len(self) > 1:
                    raise exceptions.ValidationError(_(u"There should only one default state per model"))
                else:
                    found = self.search([('default_state', '=', True), ('model_id',
                                                                        '=', self.model_id.id), ('id', '!=', self.id)])
                    for s in found:
                        s.write({'default_state': False})

        return super(State, self).write(values)
