from flask import Blueprint, request, \
                  flash, g, redirect, url_for, \
                  render_template

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from flask_wtf import Form
from wtforms import PasswordField
import wtforms.validators
from wtforms import fields
from wtforms.validators import Email, InputRequired, ValidationError

from wtforms.validators import DataRequired, Length
from adminweb.db.models import User

from flask_login import login_user, logout_user, current_user, login_required

bp = Blueprint('outside', __name__, url_prefix='/')


@bp.route('/')
def landing():
    return render_template('outside/landing.html')
