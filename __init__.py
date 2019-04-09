from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    g
)

from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy import create_engine

from flask import session as login_session

import random
import string

import json
from flask import make_response
import requests

from functools import wraps
# from flask_seasurf import SeaSurf  # cros

Base = declarative_base()


class PersonName(Base):
    __tablename__ = 'person_name'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class ResumeItem(Base):
    __tablename__ = 'resume_item'
    
    type = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    content = Column(String(2500))
    restaurant_id = Column(Integer, ForeignKey('person_name.id'))
    restaurant = relationship(PersonName, cascade="all")
    
    # We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'type': self.type,
            'content': self.content,
            'id': self.id,
        }


# engine = create_engine('sqlite:///restaurantmenu.db')

# Base.metadata.create_all(engine)

import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'client_secrets.json')
client_id = json.loads(
    open(my_file, 'r').read())['web']['client_id']
client_secret = json.loads(
    open(my_file, 'r').read())['web']['client_secret']

app = Flask(__name__)
# csrf = SeaSurf(app)

my_file = os.path.join(THIS_FOLDER, 'personalResume.db')
engine = create_engine('sqlite:///' + my_file)
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(bind=engine))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/person/<int:id>/JSON')
@app.route('/person/<int:id>.JSON')
def personJSON(id):
    session = DBSession()
    person = session.query(PersonName).filter_by(id=id).one()
    resume = session.query(ResumeItem).filter_by(restaurant_id=person.id)
    return jsonify(PersonInfo={'name': person.name}, ResumeItems=[i.serialize for i in resume])

@app.route('/person/saveName/<int:id>/<string:name>', methods=['POST'])
def personSaveName(id, name):
    session = DBSession()
    person = session.query(PersonName).filter_by(id=id).one()
    person.name = name
    session.commit()
    return jsonify({'code': 0, 'message': 'ok'})

@app.route('/person/resume/<int:resume_id>/JSON')
@app.route('/person/resume/<int:resume_id>.JSON')
def resMenuJSON(resume_id):
    session = DBSession()
    menu = session.query(ResumeItem).filter_by(id=resume_id).one()
    return jsonify(ResumeItem=menu.serialize)


@app.route('/login', methods=['GET'])
def login():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        code = request.data
        url = 'https://github.com/login/oauth/access_token?client_id='\
              + client_id\
              + '&client_secret=' + client_secret\
              + '&code=' + code
        access_token = requests.get(url).content.split('&')[0].split('=')[1]
        user_info = requests.get(
            'https://api.github.com/user?access_token=%s' % access_token)\
            .json()
        login_session['access_token'] = access_token
        login_session['username'] = user_info["login"]
        login_session['picture'] = user_info["avatar_url"]
        login_session['email'] = user_info["email"]
        login_session['bio'] = user_info["bio"]
        flash("You are now logged in as %s" % login_session['username'])
        return 'OK'


@app.route('/gdisconnect')
@app.route('/logout')
def gdisconnect():
    if login_session['access_token'] is None:
        print 'Access Token is None'
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print 'In access token is %s', login_session['access_token']
        print 'User name is: '
        print login_session['username']
        # TODO: delete access_token in github
        del login_session['access_token']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['bio']
        flash("You are now logout ")
        return redirect(url_for('all'))


if __name__ == '__main__':
    app.secret_key = 'secure key'
    app.run(host='0.0.0.0', port=5001)
