from flask import Blueprint, render_template, jsonify


od_bp = Blueprint('od', __name__, template_folder='templates')


@od_bp.route('/od')
def od():

    return render_template('od.html')


@od_bp.route('/od/<index>')
def od_index(index: str):

    return jsonify({'abc': 'edf'})


@od_bp.route('/od/<index>/<subindex>')
def od_subindex(index: str, subindex: str):

    return jsonify({'xyz': '123'})
