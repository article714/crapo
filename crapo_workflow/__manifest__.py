# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": u"Crapo: Workflow",
    "version": u"12.0.2.0.0",
    "category": u"Crapo Workflows",
    "author": u"Article714",
    "license": u"AGPL-3",
    "website": u"https://www.article714.org",
    "summary": u""" Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["queue_job", "crapo_base"],
    "data": [
        "security/workflow.xml",
        "security/workflow_activity.xml",
        "security/workflow_joiner.xml",
        "security/workflow_context_entry.xml",
        "security/workflow_context.xml",
        "security/workflow_context_joiner_event_status.xml",
        "actions/window_actions.xml",
        "views/crapo_menus.xml",
        "views/crapo_workflow_activity_views.xml",
        "views/crapo_workflow_views.xml",
        "views/crapo_workflow_joiner_event_views.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
