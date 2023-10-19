from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_uploads import UploadSet, configure_uploads, IMAGES
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, UserMixin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app)
db.init_app(app)

followers = db.Table('follower',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followee_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))
    join_date = db.Column(db.DateTime)

    tweets = db.relationship('Tweet', backref='user', lazy='dynamic')

    following = db.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followee_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    followed_by = db.relationship('User', secondary=followers,
                                  primaryjoin=(followers.c.followee_id == id),
                                  secondaryjoin=(followers.c.follower_id == id),
                                  backref=db.backref('followees', lazy='dynamic'), lazy='dynamic')


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(140))
    date_created = db.Column(db.DateTime)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'ksdlfkdsofidsithnaljnfadksjhfdskjfbnjewrhewuirhfsenfdsjkfhdksjhfdslfjasldkj'


configure_uploads(app, photos)


@app.template_filter('time_since')
def time_since(delta):
    seconds = delta.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return '%dd' % (days)
    elif hours > 0:
        return '%dh' % (hours)
    elif minutes > 0:
        return '%dm' % (minutes)
    else:
        return 'Just now'


from views import *

if __name__ == '__main__':
    app.run()
