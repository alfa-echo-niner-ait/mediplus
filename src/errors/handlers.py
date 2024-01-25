from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(401)
def error_401(error):
    code = 401
    return render_template('errors/error.html', error=error, code=code), 401

@errors.app_errorhandler(403)
def error_403(error):
    code = 403
    return render_template('errors/error.html', error=error, code=code), 403


@errors.app_errorhandler(404)
def error_404(error):
    code = 404
    return render_template('errors/error.html', error=error, code=code), 404

    
@errors.app_errorhandler(500)
def error_500(error):
    code = 500
    return render_template('errors/error.html', error=error, code=code), 500


@errors.app_errorhandler(503)
def error_503(error):
    code = 503
    return render_template('errors/error.html', error=error, code=code), 503


@errors.app_errorhandler(505)
def error_505(error):
    code = 505
    return render_template('errors/error.html', error=error, code=code), 505
    