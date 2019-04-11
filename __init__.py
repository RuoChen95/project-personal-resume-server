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
    
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


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

@app.route('/person/saveIntro/<int:id>', methods=['POST'])
def personSaveIntro(id):
    session = DBSession()
    resume = session.query(ResumeItem).filter_by(restaurant_id=id)
    for i in resume:
        if i.type == 'Description':
            i.content = json.loads(request.data)['content']
            session.commit()
            return jsonify({'code': 0, 'message': 'ok'})
        
@app.route('/person/saveWorkExperience/<int:id>', methods=['POST'])
def personSaveWorkExperience(id):
    session = DBSession()
    resume = session.query(ResumeItem).filter_by(restaurant_id=id)
    for i in resume:
        if i.type == 'Work Experience':
            i.content = json.loads(request.data)['content']
            session.commit()
            return jsonify({'code': 0, 'message': 'ok'})
        
@app.route('/person/list/JSON')
def personList():
    session = DBSession()
    person = session.query(PersonName).all()
    print person
    return jsonify(personList=[i.serialize for i in person], code=0)

@app.route('/person/resume/<int:resume_id>/JSON')
@app.route('/person/resume/<int:resume_id>.JSON')
def resMenuJSON(resume_id):
    session = DBSession()
    menu = session.query(ResumeItem).filter_by(id=resume_id).one()
    return jsonify(ResumeItem=menu.serialize)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    code = json.loads(request.data)['code']
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
    
    return jsonify({'code': 0, 'message': 'ok', 'username': login_session['username']})


@app.route('/logout')
def logout():
    del login_session['access_token']
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['bio']
    return jsonify({'code': 0, 'message': 'ok'})


if __name__ == '__main__':
    app.secret_key = 'secure key'
    app.run(host='0.0.0.0', port=5000)
