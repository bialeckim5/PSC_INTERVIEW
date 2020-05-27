from datetime import datetime
from app import db

#user model (registered determines if email otp was correctly entered yet)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(10))
    otp = db.Column(db.Integer)
    registered = db.Column(db.Boolean)
    books = db.relationship("Book", backref="users", lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, username, password):
        self.username = username
        self.password = password

#book model
class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    purchased = db.Column(db.Date(), nullable=False)
    notes = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')

    def __repr__(self):
        return '<Book %r>' % self.title

    def __init__(self, title, author, purchased, notes):
        self.title = title
        self.author = author
        self.purchased = datetime.strptime(purchased, "%Y-%m-%d")
        self.notes = notes

    def update_notes(self, notes):
        self.notes = notes

