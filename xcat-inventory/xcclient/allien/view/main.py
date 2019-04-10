###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

# from flask import Flask, request, session,
from flask import redirect, render_template, url_for

from . import console_bp
from ..nodemanager import get_nodes_list

@console_bp.route('/', methods=['GET', 'POST', 'PUT'])
def index():
    return redirect(url_for('list'))


@console_bp.route('/list')
#@login_required()
def list():
    ''' get node list '''

    data = get_nodes_list()
    return render_template('list.html', instance_list=data)


@console_bp.route('/logout')
def logout():
    return render_template('login.html')

@console_bp.route('/instance_action')
def logout():
    return render_template('login.html')

@console_bp.route('/ops_history')
def logout():
    return render_template('login.html')