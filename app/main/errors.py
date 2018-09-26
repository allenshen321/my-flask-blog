from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(404)
def not_found_page(e):
    """404错误"""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found page!'})
        response.status_code = 404
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
    return render_template('500.html'), 500


@main.app_errorhandler(403)
def forbiden(e):
    return render_template('403.html'), 403