from random import randint

import sqlalchemy

from models import User, Book
from flask import Blueprint, request, flash, redirect, url_for, session, render_template, Response
from flask_mail import *
from app import db

general_blueprint = Blueprint('general_blueprint', __name__)

#shares rendered html page of book list to email
@general_blueprint.route('/share', methods = ['GET'])
def share():
    #check login cookies for permissions
    if not check_login():
        return Response("Unauthorized", 401)

    #select user based off of both id and otp data (if one is wrong, user will be null)
    user = User.query.filter_by(id=session['id']).filter_by(otp=session['otp']).first()

    #sends rendered library message
    msg = Message('Share',sender = 'bialecki@psc.edu', recipients = [user.username])
    msg.body = render_template('library.html', books = Book.query.filter_by(user_id=user.id))
    mail = Mail(current_app)
    mail.send(msg)

    flash("Successful Share")
    return render_template('library.html', books = Book.query.filter_by(user_id=user.id))



def setup_otp(new_user):
    #OTP is produced
    otp = randint(000000,999999)
    new_user.otp = otp
    new_user.registered = False

    #OTP is sent via email
    msg = Message('OTP',sender = 'bialecki@psc.edu', recipients = [new_user.username])
    msg.body = str(otp)
    mail = Mail(current_app)
    #any failing email is still recorded in the database
    try:
        mail.send(msg)
    except:
        pass



@general_blueprint.route('/register', methods = ['GET', 'POST'])
def register():
    #registration results are posted...
    if request.method == 'POST':
        #make sure input are both valid
        if not request.form['username'] or not request.form['password']:
            flash('All fields but notes are required to register!', 'error')
        else:
            #establish new user
            new_user = User(request.form['username'], request.form['password'])
            setup_otp(new_user)
            #add new user to database
            db.session.add(new_user)
            try:
                db.session.commit()
            except:
                flash("The user was already registered")
                return redirect(url_for('auth_blueprint.logon'))
            flash("The user was registered")
            return redirect(url_for('auth_blueprint.logon'))
    return render_template('register.html')


def check_login():
    #scans id and otp session information. If no probelm return true, else return false (unauthorized access)
    try:
        session['id']
        session['otp']
        return True
    except KeyError:
        return False


@general_blueprint.route('/library')
def library():
    if not check_login():
        return Response("Unauthorized", 401)
    #renders library based off of logged in user
    user = User.query.filter_by(id=session['id']).filter_by(otp=session['otp']).first()
    return render_template('library.html', books = Book.query.filter_by(user_id=user.id))

@general_blueprint.route('/new_book', methods = ['GET', 'POST'])
def new_book():
    if not check_login():
        return Response("Unauthorized", 401)
    if request.method == 'POST':
        #integrity verification
        if not request.form['title'] or not request.form['author'] or not request.form['purchased']:
            flash('All fields but notes are required to create new book!', 'error')
        else:
            #new book is created
            new_book = Book(request.form['title'], request.form['author'],
                               request.form['purchased'], request.form['notes'])

            #book is appended to user's books
            user = User.query.filter_by(id = session['id']).filter_by(otp = session['otp']).first()
            user.books.append(new_book)

            #book itself is added to database
            db.session.add(new_book)
            db.session.commit()
            flash('This book was added to the library')
            return redirect(url_for('general_blueprint.library'))
    return render_template('new_book.html')

@general_blueprint.route('/edit_book/<id>', methods = ['GET', 'POST'])
def update_book(id):
    if not check_login():
        return Response("Unauthorized", 401)
    #user is selected, book is selected based off of both user id and book id
    user = User.query.filter_by(id = session['id']).filter_by(otp = session['otp']).first()
    book = Book.query.filter_by(id=id).filter_by(user_id=user.id).first()
    if request.method == 'POST':
        #notes are updated and commited
        book.update_notes(request.form['notes'])
        db.session.commit()
        flash('The notes for this book were updated')
        return redirect(url_for('general_blueprint.library'))
    return render_template('update_book.html', notes=book.notes)

@general_blueprint.route('/remove_book/<id>', methods = ['GET','POST'])
def remove_book(id):
    if not check_login():
        return Response("Unauthorized", 401)
    #books is selected based off of both user id and book id
    user = User.query.filter_by(id=session['id']).filter_by(otp=session['otp']).first()
    book = Book.query.filter_by(id=id).filter_by(user_id=user.id).first()
    #deletion occurs and is commited
    if request.method == 'POST':
        db.session.delete(book)
        db.session.commit()
        flash('The book was deleted')
        return redirect(url_for('general_blueprint.library'))
    return render_template('delete_book.html', id=id)