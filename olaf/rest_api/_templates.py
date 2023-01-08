import os

from flask import Blueprint, render_template

TITLE = os.uname()[1]

core_templates_bp = Blueprint('olaf_templates', __name__, template_folder='templates')


@core_templates_bp.route('/os_command')
def os_command_template():
    return render_template('os_command.html', title=TITLE, name='OS Command')


@core_templates_bp.route('/system_info')
def system_info_template():
    return render_template('system_info.html', title=TITLE, name='System Info')


@core_templates_bp.route('/updater')
def updater_template():
    return render_template('updater.html', title=TITLE, name='Updater')


@core_templates_bp.route('/fwrite')
def fwrite_template():
    return render_template('fwrite.html', title=TITLE, name='Fwrite')


@core_templates_bp.route('/fread')
def fread_template():
    return render_template('fread.html', title=TITLE, name='Fread')
