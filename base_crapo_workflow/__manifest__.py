# -*- coding: utf-8 -*-
# @author: C. Guychard
# @copyright: ©2018 Article 714
# @license: AGPL v3

{
    'name': u'Crapo: Base Module for workflow management',
    'version': u'12.0.1.0.0',
    'category': u'Crapo Workflows',
    'author': u'Article714',
    'license': u'AGPL-3',
    'website': u'https://www.article714.org',
    'summary': u' Fexible tool to manage states, transitions for your odoo objects',
    'description': u"""
Crapo: Base Module for workflow management
===========================================

Crapo is a flexible tool to manage states for your odoo models, and also provide a workflow engine.


**Credits:** .
Article714

This module include customized source code and resources from odoo source code (https://github.com/odoo/odoo)

""",
    'depends': ['queue_job'],
    'data': ['security/crapo_security.xml',
             'security/activity.xml',
             'security/crapo_action.xml',
             'security/crapo_business_object.xml',
             'security/automaton.xml',
             'security/state.xml',
             'security/transition.xml',
             'security/workflow.xml',
             'actions/window_actions.xml',
             'views/crapo_menus.xml',
             'views/crapo_state_views.xml',
             'views/crapo_transition_views.xml',
             'views/crapo_action_views.xml',
             'views/crapo_automaton_views.xml'],
    'installable': True,
    'images': [],
    'application': False,
}
