# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions


class WorkflowState(models.Model):
    """
    """
    _name = 'crapo.state'
    _description = u"State in a workflow, specific to a given model"
    _order = "sequence, name, id"

    name = fields.Char(string=_(u'Name'),
                       help=_(u"State's name"), required=True, translate=True)

    model_id = fields.Many2one(string=_(u'Model'), help=_(u"Business Model for which this state is relevant"),
                               comodel_name="ir.model",
                               )

    sequence = fields.Integer(string=_(u'Sequence'), default=1, help=_(
        u"Sequence gives the order in which states are displayed"))

    fold = fields.Boolean(string=_(u'Folded in kanban'),
                          help=_(u'This stage is folded in the kanban view when there are no records in that stage to display.'), default=False)
