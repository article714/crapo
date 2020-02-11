# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": u"Crapo: Automaton UI",
    "version": u"12.0.2.0.0",
    "category": u"Crapo Workflows",
    "author": u"Article714",
    "license": u"AGPL-3",
    "website": u"https://www.article714.org",
    "summary": u""" Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["crapo_automaton"],
    "data": [
        "actions/window_actions.xml",
        "views/crapo_menus.xml",
        "views/crapo_automaton_state_views.xml",
        "views/crapo_transition_views.xml",
        "views/crapo_automaton_action_views.xml",
        "views/crapo_automaton_views.xml",
        "views/crapo_automaton_condition_views.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
