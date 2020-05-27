from flask import Blueprint, request, flash, redirect, url_for, session, render_template, current_app, g
from flask_sqlalchemy import SQLAlchemy
from models import User, Book
from app import db
auth_blueprint = Blueprint('auth_blueprint', __name__)

# this is the root, logon node to the website
@auth_blueprint.route('/', methods = ['GET', 'POST'])
def logon():
    #if the results of the form are being posted, make sure fields have values
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('All fields but notes are required to login!', 'error')
        else:
            #filter users by the username typed, pick first
            new_user = db.session.query(User).filter_by(username=request.form['username']).first()

            #if no matching name, flash message, go to logon screen again
            if new_user == None:
                flash('No such username!')
                return redirect(url_for('auth_blueprint.logon'))
            #if passwords match...
            if new_user.password == request.form['password']:
                #... and user is not yet registered...
                if not new_user.registered:
                    #... display the verification screen
                    return redirect(url_for('auth_blueprint.verification', id=new_user.id))
                #otherwise, login.
                # SESSION ID AND OTP ARE USED JOINTLY TO MARK IDENTITY. ID WAS CONSIDERED TOO SPOOFABLE TO BE SECURE. OTP CODE CANNOT BE EASILY GUESSED.
                # IDS COULD BE GUESSED BY ADDING ONE TO ARRIVE AT ANOTHER, IF A CLIENT MODIFIES THE SESSION DATA MANUALLY IT COULD CAUSE A BREACH.
                # CLIENTS CANT MODIFY OTP EASILY TO ACHIEVE ANOTHER OTP. HOWEVER, OTP'S MAY COLLIDE SO ID IS USED TO DISAMBIGUATE
                session['id'] = new_user.id
                session['otp'] = new_user.otp
                flash('LOGGED ON!')
                return redirect(url_for('general_blueprint.library'))
            else:
                #wrong password was typed
                flash('Wrong password!')
    return render_template('logon.html')

#logout procedures
@auth_blueprint.route('/logout', methods = ['GET'])
def logout():
    #id and otp session data are wiped
    session['id'] = None
    session['otp'] = None

    #logon screen is directed to
    return redirect(url_for('auth_blueprint.logon'))

#verification screen sequence (it consists of user id box which is prefilled and then OTP code which was emailed)
@auth_blueprint.route('/verification/<id>', methods = ['GET', 'POST'])
def verification(id):
    #if results of form are being posted..
    if request.method == 'POST':
        #if otp is not present or id is not present, flash error
        if not request.form['otp']:
            flash('All fields but notes are required to login!', 'error')
        else:
            #otherwise, find user by id
            new_user = db.session.query(User).filter_by(id=id).first()

            #if user is not registered, go to logon screen
            if new_user == None:
                flash('No such id!')
                return redirect(url_for('auth_blueprint.logon'))
            #if user registered already, flash message
            if new_user.registered:
                flash("Already registered")
                return redirect(url_for('auth_blueprint.logon'))
            #if otp matched, switch registered boolean to true, mark session data with id and otp
            if new_user.otp == int(request.form['otp']):
                session['id'] = new_user.id
                session['otp'] = new_user.otp
                new_user.registered = True

                db.session.commit()
                flash('LOGGED ON!')
                return redirect(url_for('general_blueprint.library'))
            else:
                #if not a otp match
                flash('Wrong code!')
    return render_template('verification.html', id=id)