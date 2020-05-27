# Matthew Bialecki
# 27 May 2020
# Booklist Flask Application

#Purpose: to create a flask web-based application which allows for the addition, deletion and editing of books
#           SQLite and SQLAlchemy update results in real time. Email outputs are used for verification of account,
#           and to share the book list via email.

import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


#initialization of flask app
app = Flask(__name__)

#mail settings (please don't hack me)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.sqlite3'
app.config['SECRET_KEY'] =  os.urandom(12)
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'bialecki@psc.edu'
app.config['MAIL_PASSWORD'] = 'pscrocks2020'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#establishment of SQLAlchemy connection
db = SQLAlchemy(app)
db.init_app(app)

#these import statements MUST occur below the SQLAlchemy statements
#these statements import the models
from auth_blueprint import auth_blueprint
from general_blueprint import general_blueprint

#the authentication and general blueprints are registeed
app.register_blueprint(auth_blueprint)
app.register_blueprint(general_blueprint)

#migration settings are established here (python app.py db performs migration commands)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

#in case of empty database, python app.py createdb --creates the database representation of the models
@manager.command
def createdb():
    db.create_all()

#default is to always create tables on startput
db.create_all()
if __name__ == '__main__':
    # app.run(debug=True)

    #manager is run to start flask app
    manager.run()

