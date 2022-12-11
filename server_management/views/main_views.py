from flask import Blueprint, url_for
from werkzeug.utils import redirect
from datetime import datetime
from flask import Blueprint, url_for, render_template, flash, request, session, g
from flask import Blueprint, render_template, request, url_for
from werkzeug.utils import redirect

from server_management import db
from server_management.forms import UserCreateForm, UserLoginForm
from server_management.models import User

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'


@bp.route('/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('question._list'))
        flash(error)
    return render_template('auth/login.html', form=form)
