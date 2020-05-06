# pylint: disable=missing-docstring
{
    "name": "Crapo: Workflow",
    "version": "12.0.3.0.0",
    "category": "Crapo Automata & Workflows",
    "author": "Article714",
    "license": "LGPL-3",
    "website": "https://www.article714.org",
    "summary": """ Create and manage workflows """,
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
