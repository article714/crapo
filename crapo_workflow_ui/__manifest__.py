# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": "Crapo: Workflow UI",
    "version": "12.0.2.0.0",
    "category": "Crapo Workflows",
    "author": "Article714",
    "license": "AGPL-3",
    "website": "https://www.article714.org",
    "summary": """ Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["crapo_workflow", "web_tree_dynamic_colored_field"],
    "data": [
        "actions/window_actions.xml",
        "views/crapo_menus.xml",
        "views/crapo_workflow_activity_views.xml",
        "views/crapo_workflow_views.xml",
        "views/crapo_workflow_event_views.xml",
        "views/crapo_workflow_trigger_views.xml",
        "views/crapo_workflow_context_views.xml",
        "security/workflow_diagram.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
