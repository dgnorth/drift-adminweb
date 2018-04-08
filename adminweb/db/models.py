from sqlalchemy import Column, Integer, String, DateTime, Unicode, ForeignKey
from sqlalchemy import BigInteger, Boolean, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.schema import Sequence, Index
from drift.orm import ModelBase, utc_now
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash


class User(ModelBase):
    __tablename__ = 'dsp_users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    full_name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password_hash = Column(String(200))
    login_date = Column(DateTime, nullable=True)
    prev_login_date = Column(DateTime, nullable=True)
    num_logins = Column(Integer, default=0)

    status = Column(String(20), nullable=True, default="active")

    roles = relationship('WebUserRole', backref=backref('dsp_users', uselist=True))

    def __init__(self, username, password, full_name="", email=""):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_property
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    @hybrid_property
    def id(self):
        return self.user_id

    def get_id(self):
        return unicode(self.user_id)

    def __repr__(self):
        return '<User %r (%s)>' % (self.username, self.user_id)


class WebUserRole(ModelBase):
    __tablename__ = 'dsp_userroles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('dsp_users.user_id', ondelete='CASCADE'))
    role = Column(String(20), nullable=False)


class LogUserLogin(ModelBase):
    __tablename__ = 'dsp_log_userlogins'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('dsp_users.user_id'), nullable=False, index=True)
    ip_address = Column(String(20))


class LogAction(ModelBase):
    __tablename__ = 'dsp_log_actions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('dsp_users.user_id'), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False, server_default='info')
    details = Column(JSON, nullable=True)
    reference_id = Column(Integer, nullable=True, index=True)
    reference_type = Column(String(50), nullable=True, index=True)

    user = relationship(User, backref=backref('dsp_log_actions', uselist=False))


class PlayerInfo(ModelBase):
    __tablename__ = 'dsp_player_info'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, index=True)
    admin_user_id = Column(Integer, index=True)
    notes = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
