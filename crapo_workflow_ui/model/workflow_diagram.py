"""
see README for details
"""
from odoo import tools
from odoo import models, fields, api


class WorkflowDiagramNode(models.Model):
    """
    A node in the diagram
    """

    _name = "crapo.workflow.diagram.node"
    _auto = False

    id = fields.Integer()

    workflow_id = fields.Many2one("crapo.workflow")

    name = fields.Char()

    from_arrow_ids = fields.One2many(
        "crapo.workflow.diagram.arrow", "from_node"
    )
    to_arrow_ids = fields.One2many("crapo.workflow.diagram.arrow", "to_node")

    @api.model_cr
    def init(self):
        """
        Actions to be taken on module installation
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
            CREATE OR REPLACE VIEW crapo_workflow_diagram_node AS (
                SELECT
                    ('1' || act.id)::int id,
                    act.workflow_id,
                    '⚙ -- ' || ir.name "name"
                FROM
                    crapo_workflow_activity act
                    join ir_act_server ir on ir.id = action_server_id
                UNION ALL
                SELECT
                    ('2' || trg.id)::int id,
                    trg.workflow_id,
                    '◇ -- ' || trg.name "name"
                FROM
                    crapo_workflow_trigger trg
                UNION ALL
                SELECT
                    ('3' || evt.id)::int id,
                    trg.workflow_id,
                    '✉ -- ' || evt.name "name"
                FROM
                    crapo_workflow_event evt
                    JOIN crapo_workflow_trigger trg ON trg.id = evt.trigger_id
                WHERE
                    evt.event_type != 'activity_ended'

            );"""
        self.env.cr.execute(query)


class WorkflowDiagramArrow(models.Model):
    """
    A link (arrow: directed link) in the diagram
    """

    _name = "crapo.workflow.diagram.arrow"
    _auto = False

    id = fields.Integer()

    workflow_id = fields.Many2one("crapo.workflow")

    from_node = fields.Many2one("crapo.workflow.diagram.node")

    to_node = fields.Many2one("crapo.workflow.diagram.node")

    @api.model_cr
    def init(self):
        """
        actions to take when creating tables on module initialization or
        installation
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
            CREATE OR REPLACE VIEW crapo_workflow_diagram_arrow AS (
                SELECT
                    row_number() over() id,
                    workflow_id,
                    from_node::int,
                    to_node::int
                FROM
                    (

                    SELECT
                        trg.workflow_id,
                        '1' || tj.crapo_workflow_activity_id from_node,
                        '2' || tj.crapo_workflow_trigger_id to_node
                    FROM
                        crapo_workflow_tj_activity_trigger tj
                        JOIN crapo_workflow_trigger trg ON (
                            tj.crapo_workflow_trigger_id = trg.id)
                    UNION ALL
                    SELECT
                        act.workflow_id,
                        '2' || tj.crapo_workflow_trigger_id from_node,
                        '1' || tj.crapo_workflow_activity_id to_node

                    FROM
                        crapo_workflow_tj_trigger_activity tj
                        JOIN crapo_workflow_activity act ON (
                            tj.crapo_workflow_activity_id = act.id)
                    UNION ALL
                    SELECT
                        trg.workflow_id,
                        '3' || evt.id from_node,
                        '2' || evt.trigger_id to_node
                    FROM
                        crapo_workflow_event evt
                        JOIN crapo_workflow_trigger trg
                             ON trg.id = evt.trigger_id
                    WHERE
                        evt.event_type != 'activity_ended'

                    ) a
            );"""
        self.env.cr.execute(query)
