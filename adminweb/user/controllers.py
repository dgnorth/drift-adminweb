import os

from flask import Blueprint, request, \
                  flash, g, redirect, url_for, \
                  render_template, current_app

from flask_wtf import Form
from wtforms import fields
from wtforms.validators import Email, InputRequired, ValidationError, Length

from adminweb.db.models import User, LogUserLogin, LogAction, WebUserRole
from flask_login import login_user, logout_user
from adminweb.utils import log_action, role_required

import datetime, random, string

bp = Blueprint('user', __name__, url_prefix='/admin/')

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'test')


def create_password():
    password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return password


def create_admin(username, password):
    user = User(username, password)
    g.db.add(user)
    g.db.flush()
    role = WebUserRole(user_id=user.user_id, role='roleadmin')
    g.db.add(role)
    role = WebUserRole(user_id=user.user_id, role='useradmin')
    g.db.add(role)
    role = WebUserRole(user_id=user.user_id, role='admin')
    g.db.add(role)
    g.db.commit()

    return user


class LoginForm(Form):
    username = fields.StringField(validators=[InputRequired()])
    password = fields.StringField(validators=[InputRequired()])

    def validate_username(form, field):
        user = g.db.query(User).filter(User.username == form.username.data, User.status == 'active').first()
        if form.username.data == ADMIN_USERNAME and form.password.data == ADMIN_PASSWORD:
            if not current_app.debug:
                raise ValidationError("Admin override only allowed when running DEBUG")
            if user:
                user.set_password(ADMIN_PASSWORD)
            else:
                user = create_admin(ADMIN_USERNAME, ADMIN_PASSWORD)
            g.db.commit()
        elif user is None:
            raise ValidationError("User not found")
        form.user = user

    def validate_password(form, field):
        user = g.db.query(User).filter(User.username == form.username.data).first()
        if not user or not user.check_password(form.password.data):
            raise ValidationError("Invalid password")
        form.user = user


def update_user_login():
    if not g.user.is_authenticated:
        return
    g.user.num_logins += 1
    g.user.prev_login_date = g.user.login_date
    g.user.login_date = datetime.datetime.utcnow()

    log_row = LogUserLogin(user_id=g.user.user_id, ip_address=request.remote_addr)
    g.db.add(log_row)
    g.db.commit()


@bp.route('login', methods=['GET', 'POST'])
def login():
    if g.user and g.user.is_authenticated:
        update_user_login()
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        update_user_login()
        return redirect(request.args.get('next') or url_for('dashboard.index'))
    return render_template('user/login.html', form=form)


@bp.route('logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('outside.landing'))


@bp.route('settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if request.form['change_password']:
            if request.form['change_password'] != request.form['change_password2']:
                flash('Passwords do not match')
                return redirect(request.referrer)
            g.user.set_password(request.form['change_password'])
        g.user.full_name = request.form['change_full_name']
        g.user.email = request.form['change_email']

        g.db.commit()
        flash('User Settings have been updated')
        return redirect(url_for('dashboard.index'))
    return render_template('user/settings.html')


@bp.route('users', methods=['GET'])
def users():
    rows = g.db.query(User).order_by(User.username)
    return render_template('user/list.html', users=rows)


@bp.route('users/<int:user_id>', methods=['GET'])
def user(user_id):
    user = g.db.query(User).get(user_id)
    return render_template('user/lookup.html', user=user)


@bp.route('users/loginlog', methods=['GET'])
def loginlog():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    query = g.db.query(LogUserLogin, User).filter(LogUserLogin.user_id==User.id)
    if request.args.get('user_id'):
        query = query.filter(LogUserLogin.user_id==int(request.args.get('user_id')))
    query = query.order_by(LogUserLogin.id.desc())
    row_count = query.count()
    query = query.limit(page_size)
    query = query.offset(offset)
    num_pages = int(row_count/page_size)+1

    return render_template('user/loginlog.html', rows=query,
                        num_pages=num_pages,
                        curr_page=curr_page)


@bp.route('users/actionlog', methods=['GET'])
def actionlog():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    query = g.db.query(LogAction, User).filter(LogAction.user_id==User.id)
    if request.args.get('user_id'):
        query = query.filter(LogAction.user_id==int(request.args.get('user_id')))
    query = query.order_by(LogAction.id.desc())
    row_count = query.count()
    query = query.limit(page_size)
    query = query.offset(offset)
    num_pages = int(row_count/page_size)+1

    return render_template('user/actionlog.html', rows=query,
                        num_pages=num_pages,
                        curr_page=curr_page)


@bp.route('users/<int:user_id>/resetpassword', methods=['GET', 'POST'])
@role_required('useradmin')
def resetpassword(user_id):
    user = g.db.query(User).get(user_id)
    password = ""
    if request.form.get('change'):
        password = create_password()
        user.set_password(password)
        g.db.commit()
        log_action('adminuser.resetpassword', ref=('adminuser', user_id))
    return render_template('user/resetpassword.html', user=user, password=password)


@bp.route('users/<int:user_id>/enable', methods=['GET'])
@role_required('useradmin')
def enable(user_id):
    user = g.db.query(User).get(user_id)
    user.status = 'active'
    g.db.commit()
    log_action('adminuser.userenabled', ref=('adminuser', user_id))
    return redirect(request.referrer)


@bp.route('users/<int:user_id>/disable', methods=['GET'])
@role_required('useradmin')
def disable(user_id):
    user = g.db.query(User).get(user_id)
    user.status = 'disabled'
    g.db.commit()
    log_action('adminuser.userdisabled', ref=('adminuser', user_id))
    return redirect(request.referrer)


@bp.route('users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required('useradmin')
def edit(user_id):
    user = g.db.query(User).get(user_id)
    if request.method == 'POST':
        new_full_name = request.form.get('set_full_name')
        new_username = request.form.get('set_username').lower()
        new_email = request.form.get('set_email')
        new_password = request.form.get('set_password')
        if not new_username:
            flash('Username cannot be blank!')
            return redirect(request.referrer)
        details = {}
        if user.full_name != new_full_name:
            details['old_full_name'] = user.full_name
            details['new_full_name'] = new_full_name
        if user.email != new_email:
            details['old_email'] = user.email
            details['new_email'] = new_email
        if user.username != new_username:
            details['old_username'] = user.username
            details['new_username'] = new_username

        if new_password:
            details['password_changed'] = True

        user.full_name = new_full_name
        user.username = new_username
        user.email = new_email
        if new_password:
            user.set_password(new_password)
        g.db.commit()
        flash('User has been changed')
        log_action('adminuser.edituser', ref=('adminuser', user_id), details=details)
        return redirect(url_for('user.lookup', user_id=user_id))
    return render_template('user/edituser.html',
                           username=user.username,
                           full_name=user.full_name,
                           email=user.email,
                           user_id=user.user_id)


@bp.route('users/new', methods=['GET', 'POST'])
@role_required('useradmin')
def new():
    if request.method == 'POST':
        new_full_name = request.form.get('set_full_name')
        new_username = request.form.get('set_username').lower()
        new_email = request.form.get('set_email')
        new_password = request.form.get('set_password')
        if not new_username:
            flash('Username cannot be blank!')
            return redirect(request.referrer)
        if not new_password:
            flash('Password cannot be blank!')
            return redirect(request.referrer)
        user = User(new_username, new_password, new_full_name, new_email)
        g.db.add(user)
        g.db.commit()
        user_id = user.user_id
        flash('User has been created')
        log_action('adminuser.adduser', ref=('adminuser', user_id))
        return redirect(url_for('user.user', user_id=user_id))
    return render_template('user/edituser.html')


@bp.route('users/<int:user_id>/editroles', methods=['GET', 'POST'])
@role_required('roleadmin')
def editroles(user_id):
    all_roles = [r[0] for r in current_app.config.get('admin_roles')]
    user = g.db.query(User).get(user_id)
    user_roles = set([r.role for r in user.roles])
    new_roles = set()
    if request.method == 'POST':
        for role in all_roles:
            if request.form.get(role):
                new_roles.add(role)

        roles_to_remove = user_roles - new_roles
        roles_to_add = new_roles - user_roles
        for role in roles_to_remove:
            for r in user.roles:
                if r.role == role:
                    g.db.delete(r)
        for role in roles_to_add:
            r = WebUserRole(user_id=user_id, role=role)
            g.db.add(r)
        g.db.commit()
        flash('User roles has been changed')
        if roles_to_add or roles_to_remove:
            details = {}
            if roles_to_add:
                details["added_roles"] = ", ".join(roles_to_add)
            if roles_to_remove:
                details["removed_roles"] = ", ".join(roles_to_remove)
            log_action('adminuser.edituserroles', ref=('adminuser', user_id), details=details)
        return redirect(url_for('user.user', user_id=user_id))
    return render_template('user/editroles.html',
                           user=user,
                           admin_roles=current_app.config.get('admin_roles'),
                           roles=user_roles)
