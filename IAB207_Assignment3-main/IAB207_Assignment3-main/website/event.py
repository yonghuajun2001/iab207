from flask import Blueprint, flash, render_template, request, url_for, redirect
from .models import User, Event, Order, Comment
from .forms import EventForm, CommentForm, BookingForm, UpdateEventForm
from flask_login import current_user, login_required
from . import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

#create blueprint
eventbp = Blueprint('event', __name__, url_prefix='/events')

@eventbp.route('/<int:event_id>')
def show(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))
    # Create the comment form
    cform = CommentForm()
    bform = BookingForm()

    return render_template('event/show.html', event=event, commentform=cform, bookingform=bform)

@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    create = EventForm()
    create.event_category.choices = [
        ('Charity Run', 'Charity Run'),
        ('Charity Auction', 'Charity Auction'),
        ('Charity Food Donation', 'Charity Food Donation'),
        ('Others', 'Others')
    ]

    if create.validate_on_submit():
        db_file_path = check_upload_file(create)
        event_status = determine_event_status(create)


        new_event = Event(
            event_name=create.event_name.data,
            event_location=create.event_location.data,
            event_date=create.event_date.data,
            event_time=create.event_time.data,
            event_description=create.event_description.data,
            event_category=create.event_category.data,
            event_image=db_file_path,
            event_ticket_quantity=create.event_ticket_quantity.data,
            event_ticket_price=create.event_ticket_price.data,
            event_status=event_status,
            user=current_user
        )

        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('event/update.html', form=create, heading='create')


def check_upload_file(form):
    # get file data from form
    fp = form.image.data
    filename = fp.filename
    # get the current path of the module file… store image file relative to this path
    BASE_PATH = os.path.dirname(__file__)
    # upload file location – directory of this file/static/image
    upload_path = os.path.join(BASE_PATH, 'static/image', secure_filename(filename))
    # store relative path in DB as image location in HTML is relative
    db_upload_path = '/static/image/' + secure_filename(filename)
    # save the file and return the db upload path
    fp.save(upload_path)
    return db_upload_path


def determine_event_status(form):
    if form.event_ticket_quantity.data == 0:
        return 'Sold Out'
    elif form.event_date.data < datetime.now().date():
        return 'Inactive'
    else:
        return 'Open'

@eventbp.route('/<int:event_id>/invalidbooking', methods=['GET', 'POST'])
def disablebooking(event_id):
     event = Event.query.filter_by(id=event_id).first()
     flash('Booking not allowed', 'error')
     return redirect(url_for('event.show', event_id=event.id))


# Update Event
@eventbp.route('/<int:event_id>/update', methods=['GET', 'POST'])
@login_required
def update(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))

    if event.user != current_user:
        flash('You do not have permission to update this event', 'error')
        return redirect(url_for('event.show', event_id=event.id))

    form = UpdateEventForm(obj=event)
    if form.validate_on_submit():
        event_status = determine_event_status(form)
        db_file_path = check_upload_file(form)  # Add this line to get the file path

        form.populate_obj(event)  # Update the event object with form data
        event.event_image = db_file_path  # Set the updated file path
        event.event_status = event_status  # Set the updated event status
        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('event.show', event_id=event.id))

    return render_template('event/update.html', form=form, event=event, heading='update')


# Cancel Event
@eventbp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))

    if event.user != current_user:
        flash('You do not have permission to cancel this event', 'error')
        return redirect(url_for('event.show', event_id=event.id))

    event.event_status = 'Cancelled'
    db.session.commit()

    flash('Event cancelled successfully!', 'success')
    return redirect(url_for('event.show', event_id=event.id))


@eventbp.route('/<int:event_id>/open', methods=['POST'])
@login_required
def open(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))

    if event.user != current_user:
        flash('You do not have permission to cancel this event', 'error')
        return redirect(url_for('event.show', event_id=event.id))

    event.event_status = 'Open'
    db.session.commit()

    flash('Event opened successfully!', 'success')
    return redirect(url_for('event.show', event_id=event.id))


# Booking Event Ticket
@eventbp.route('/<int:event_id>/booking', methods=['GET', 'POST'])
@login_required
def booking(event_id):
    event = Event.query.filter_by(id=event_id).first()
    form = BookingForm(obj=event)
    if form.validate_on_submit():
        ticket_no = form.ticket_required.data
        if ticket_no > event.event_ticket_quantity:
            flash('Invalid ticket number insert', 'failed')
        else:
            if event.event_ticket_quantity == ticket_no:
                event.event_ticket_quantity = 0
                event.event_status = 'Sold Out'
            else:
                event.event_ticket_quantity = event.event_ticket_quantity - ticket_no
            booking = Order(
                event=event,
                user=current_user,
                number_of_tickets=ticket_no,
            )
            # commit to the database
            db.session.add(booking)
            db.session.commit()
            flash('Successfully booked, booking details have been added', 'success')
            # Always end with redirect when form is valid
            return redirect(url_for('main.history'))
    return render_template('event/update.html', form=form, event=event, heading='booking')


# Comment
@eventbp.route('/<int:event_id>/comment', methods=['GET', 'POST'])
@login_required
def comment(event_id):
    form = CommentForm()
    event = Event.query.filter_by(id=event_id).first()
    if form.validate_on_submit():
        new_comment = Comment(comment=form.text.data, user=current_user, event=event)
        db.session.add(new_comment)
        db.session.commit()

        flash('Comment added successfully!', 'success')
        return redirect(url_for('event.show', event_id=event.id))  # Redirect to the event show page

    return render_template('event/show.html', commentform=form, event=event)
