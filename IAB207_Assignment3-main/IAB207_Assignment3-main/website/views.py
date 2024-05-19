from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from .models import Event, Order, User
from . import db
from datetime import datetime

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)


@bp.route('/search')
def search():
    if request.args['search']:
        search = '%' + request.args['search'] + '%'
        events = Event.query.filter(Event.event_category.like(search)).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))


@bp.route('/all')
def all():
    return redirect(url_for('main.index'))


@bp.route('/run')
def run():
    search = '%' + 'run' + '%'
    events = Event.query.filter(Event.event_category.like(search)).all()
    return render_template('index.html', events=events)


@bp.route('/auction')
def auction():
    search = '%' + 'auction' + '%'
    events = Event.query.filter(Event.event_category.like(search)).all()
    return render_template('index.html', events=events)


@bp.route('/donation')
def donation():
    search = '%' + 'donation' + '%'
    events = Event.query.filter(Event.event_category.like(search)).all()
    return render_template('index.html', events=events)


@bp.route('/other')
def other():
    search = '%' + 'other' + '%'
    events = Event.query.filter(Event.event_category.like(search)).all()
    return render_template('index.html', events=events)


@bp.route('/history')
@login_required
def history():
    user_id = current_user.id
    order = Order.query.filter(Order.user_id.like(user_id)).all()
    return render_template('history.html', orders=order)


@bp.route('/searchOrder')
def search_order():
    if request.args['search_order']:
        search = '%' + request.args['search_order'] + '%'
        user_id = current_user.id
        order = (
            db.session.query(Order)
            .join(Event)
            .filter(Order.user_id == user_id, Event.event_name.like(search))
            .all()
        )
        return render_template('history.html', orders=order)
    else:
        return redirect(url_for('main.history'))


