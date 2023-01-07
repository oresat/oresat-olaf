import os

from flask import Blueprint, render_template

TITLE = os.uname()[1]

core_templates_bp = Blueprint('olaf_templates', __name__, template_folder='templates')


@core_templates_bp.route('/os_command')
def os_command_template():
    return render_template('os_command.html', title=TITLE)


@core_templates_bp.route('/system_info')
def system_info_template():
    return render_template('system_info.html', title=TITLE)


@core_templates_bp.route('/updater')
def updater_template():
    return render_template('updater.html', title=TITLE)
