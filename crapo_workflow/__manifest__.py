# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": "Crapo: Workflow",
    "version": "12.0.2.0.0",
    "category": "Crapo Workflows",
    "author": "Article714",
    "license": "AGPL-3",
    "website": "https://www.article714.org",
    "summary": """ Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["queue_job", "crapo_base"],
    "data": [
        "security/workflow.xml",
        "security/workflow_activity.xml",
        "security/workflow_trigger.xml",
        "security/workflow_context_entry.xml",
        "security/workflow_context.xml",
        "security/workflow_context_event.xml",
        "security/workflow_broker.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
