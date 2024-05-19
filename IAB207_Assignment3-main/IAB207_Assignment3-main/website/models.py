from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    emailid = db.Column(db.String(100), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.String(100),index=True,nullable=False)

    event = db.relationship('Event', backref='User')
    order = db.relationship('Order', backref='User')
    comment = db.relationship('Comment', backref='User')


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), index=True, nullable=False)
    event_location = db.Column(db.String, nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    event_description = db.Column(db.String(250), nullable=False)
    event_category = db.Column(db.String(50), nullable=False)
    event_image = db.Column(db.String(400), nullable=False)
    event_ticket_quantity = db.Column(db.Integer, nullable=False)
    event_ticket_price = db.Column(db.Float, nullable=False)
    event_status = db.Column(db.String(50), nullable=False)

    #add foreign key 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User', backref='Event')
    comments = db.relationship('Comment', backref='Event')

    def __repr__(self): #string print method
        return "<Name: {}>".format(self.name)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.Date, default=datetime.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    user = db.relationship('User', backref='Comment')
    event = db.relationship('Event', backref='Comment') 

    def get_time(self):
        return self.created_at.strftime("%d/%m/%Y")

    def __repr__(self):
        return "<Comment: {}>".format(self.text)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, index=True, primary_key=True)
    date_ordered = db.Column(db.Date, nullable=False, default=datetime.now())
    number_of_tickets = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    user = db.relationship('User', backref='Order')
    event = db.relationship('Event', backref='Order') 
    def get_time_nice(self):
        return self.date_ordered.strftime("%Y/%m/%d")    