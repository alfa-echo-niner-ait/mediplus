from flask import Blueprint, render_template

error = Blueprint('error', __name__)

@error.app_errorhandler(401)
def error_401(error):
    code = 401
    return render_template('error/error.html', error=error, code=code), 401

@error.app_errorhandler(403)
def error_403(error):
    code = 403
    return render_template('error/error.html', error=error, code=code), 403


@error.app_errorhandler(404)
def error_404(error):
    code = 404
    return render_template('error/error.html', error=error, code=code), 404


@error.app_errorhandler(405)
def error_405(error):
    code = 405
    return render_template('error/error.html', error=error, code=code), 405

    
@error.app_errorhandler(500)
def error_500(error):
    code = 500
    return render_template('error/error.html', error=error, code=code), 500


@error.app_errorhandler(503)
def error_503(error):
    code = 503
    return render_template('error/error.html', error=error, code=code), 503


@error.app_errorhandler(505)
def error_505(error):
    code = 505
    return render_template('error/error.html', error=error, code=code), 505
    