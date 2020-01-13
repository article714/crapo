# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": u"Crapo: Automaton",
    "version": u"12.0.2.0.0",
    "category": u"Crapo Workflows",
    "author": u"Article714",
    "license": u"AGPL-3",
    "website": u"https://www.article714.org",
    "summary": u""" Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["queue_job", "crapo_base"],
    "data": [
        "security/crapo_security.xml",
        "security/crapo_action.xml",
        "security/crapo_business_object.xml",
        "security/automaton.xml",
        "security/automaton_transition.xml",
        "security/condition.xml",
        "security/state.xml",
        "security/workflow.xml",
        "security/workflow_activity.xml",
        "security/workflow_transition.xml",
        "security/workflow_joiner.xml",
        "security/workflow_context_entry.xml",
        "actions/window_actions.xml",
        "views/crapo_menus.xml",
        "views/crapo_state_views.xml",
        "views/crapo_transition_views.xml",
        "views/crapo_action_views.xml",
        "views/crapo_workflow_activity_views.xml",
        "views/crapo_automaton_views.xml",
        "views/crapo_condition_views.xml",
        "views/crapo_workflow_views.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
