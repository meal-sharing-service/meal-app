from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, OfferForm, EmptyForm
from app.models import User, Offer
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer(
            title=form.title.data,
            body=form.body.data,
            servings=form.servings.data,
            expiration=form.expiration.data,
            category_id=form.category_id.data,
            condition=form.condition.data,
            request=form.request.data, 
            author=current_user)
        db.session.add(offer)
        db.session.commit()
        flash('Your offer is now live!')
        return redirect(url_for('explore'))
    offers = Offer.query.order_by(Offer.timestamp.desc()).all()
    return render_template('explore.html', title='Home', form=form, offers=offers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('explore')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            state_province=form.state_province.data,
            country=form.country.data,
            username=form.username.data, 
            email=form.email.data,
            interest=form.interest.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()
    offers = user.offers.all()
    return render_template('user.html', user=user, offers=offers, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.first_name=form.first_name.data
        current_user.last_name=form.last_name.data
        current_user.address=form.address.data
        current_user.postal_code=form.postal_code.data
        current_user.state_province=form.state_province.data
        current_user.country=form.country.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.address.data = current_user.address
        form.postal_code.data = current_user.postal_code
        form.state_province.data = current_user.state_province
        form.country.data = current_user.country
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/offer/<id>')
@login_required
def offer(id):
    form = EmptyForm()
    offer = get_offer(id,check_author=False)
    user = User.query.filter_by(username=offer.author.username).first
    return render_template('offer.html', user=user, offer=offer, form=form)

@app.route('/offer/<id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    offer = get_offer(id)
    form = OfferForm()
    if form.validate_on_submit():
        offer.title = form.title.data
        offer.body = form.body.data
        offer.servings = form.servings.data
        offer.expiration = form.expiration.data
        offer.category_id = form.category_id.data
        offer.condition = form.condition.data
        offer.request = form.request.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('offer', id=offer.id))
    elif request.method == 'GET':
        form.title.data = offer.title
        form.body.data = offer.body
        form.servings.data = offer.servings
        form.expiration.data = offer.expiration
        form.category_id.data = offer.category_id
        form.condition.data = offer.condition
        form.request.data = offer.request
    return render_template('update_offer.html', form=form)

@app.route('/offer/<id>/delete', methods=['POST'])
@login_required
def delete(id):
    form = EmptyForm()
    offer = get_offer(id)
    if form.validate_on_submit():
        db.session.delete(offer)
        db.session.commit()
        flash('Offer deleted.')
    return redirect(url_for('user', username=offer.author.username))

def get_offer(id, check_author=True):
    offer = Offer.query.get(id)

    if offer is None:
        abort(404, "Offer id {0} doesn't exist.".format(id))

    if check_author and offer.author.username != current_user.username:
        abort(403)

    return offer