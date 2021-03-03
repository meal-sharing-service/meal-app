from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, OfferForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm, EditOfferForm, RequestForm, MessageForm
from app.models import User, Offer, Order, Message
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from json import loads
from requests import get


SPOONACULAR_APIKEY = "c917e235c7cd4c389ffc901c220f86d8"
COMPLEX_SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch"
APIKEY_PARAM = "?apikey="+SPOONACULAR_APIKEY
DEFAULT_SEARCH_BATCH = 10


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/explore')
def explore():
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    offers = Offer.query.order_by(Offer.timestamp.desc()).paginate(
        page, app.config['OFFERS_PER_PAGE'], False)
    next_url = url_for('explore', page=offers.next_num) \
        if offers.has_next else None
    prev_url = url_for('explore', page=offers.prev_num) \
        if offers.has_prev else None
    return render_template('explore.html', title='Explore', offers=offers.items, form=form, 
                            next_url=next_url, prev_url=prev_url)


@app.route('/offer/create_offer', methods=['GET', 'POST'])
@login_required
def create_offer():
    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer(
            title=form.title.data,
            body=form.body.data,
            pickup=form.pickup.data,
            servings=form.servings.data,
            expiration=form.expiration.data,
            category_id=form.category_id.data,
            condition=form.condition.data,
            request=False, 
            author=current_user)
        db.session.add(offer)
        db.session.commit()
        flash('Your offer is now live!')
        return redirect(url_for('explore'))
    return render_template('create_offer.html', title='Share Food', form=form)


@app.route('/offer/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    form = RequestForm()
    if form.validate_on_submit():
        offer = Offer(
            title=form.title.data,
            body=form.body.data,
            pickup=form.pickup.data,
            servings=form.servings.data,
            expiration=form.expiration.data,
            category_id=form.category_id.data,
            condition=form.condition.data,
            request=True, 
            author=current_user)
        db.session.add(offer)
        db.session.commit()
        flash('Your request is now live!')
        return redirect(url_for('explore'))
    return render_template('create_request.html', title='Request Food', form=form)


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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


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
    offers = user.offers.order_by(Offer.timestamp.desc()).all()
    orders = user.orders.order_by(Order.timestamp.desc()).all()
    return render_template('user.html', user=user, offers=offers, form=form, orders=orders)


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
def offer(id):
    form = EmptyForm()
    offer = get_offer(id,check_author=False)
    user = User.query.filter_by(username=offer.author.username).first
    return render_template('offer.html', user=user, offer=offer, form=form)


@app.route('/offer/<id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    offer = get_offer(id)
    form = EditOfferForm()
    if form.validate_on_submit():
        offer.body = form.body.data
        offer.pickup = form.pickup.data
        offer.category_id = form.category_id.data
        offer.condition = form.condition.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('offer', id=offer.id))
    elif request.method == 'GET':
        form.body.data = offer.body
        form.pickup.data = offer.pickup
        form.category_id.data = offer.category_id
        form.condition.data = offer.condition
    return render_template('update_offer.html', form=form, offer=offer)


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


@app.route('/offer/<id>/claim', methods=['POST'])
@login_required
def claim(id):
    form = EmptyForm()
    offer = get_offer(id,check_author=False)
    if form.validate_on_submit():
        order = Order(
            user_id = current_user.id,
            offer_id = offer.id
            )
        offer.claims += 1
        db.session.add(order)
        db.session.commit()
        flash('Offer claimed!')
    return redirect(url_for('offer', id=offer.id))


@app.route('/offer/<id>/unclaim', methods=['POST'])
@login_required
def unclaim(id):
    form = EmptyForm()
    offer = get_offer(id,check_author=False)
    order = get_order(id)
    if form.validate_on_submit():
        offer.claims -= 1
        db.session.delete(order)
        db.session.commit()
        flash('Claim deleted.')
    return redirect(url_for('explore'))


@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('user', username=user.username))
    return render_template('send_message.html', title='Send Message',
                           form=form, recipient=recipient)


@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, app.config['OFFERS_PER_PAGE'], False)
    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


def get_offer(id, check_author=True):
    offer = Offer.query.get(id)

    if offer is None:
        abort(404, "Offer id {0} doesn't exist.".format(id))

    if check_author and offer.author.username != current_user.username:
        abort(403)

    return offer


def get_order(id):
    offer = Offer.query.get(id)
    if offer is None:
        abort(404, "Offer id {0} doesn't exist.".format(id))

    orders = offer.orders
    
    for order in orders:
        if order.user_id == current_user.id:
            return order
    abort(403)


def search_recipe(query, parameters):

    string = COMPLEX_SEARCH_URL + APIKEY_PARAM + "&query=" + query

    if parameters is not None:
        for parameter in parameters:
            string = string + "&" + parameter

    string = string + "&number=" + str(DEFAULT_SEARCH_BATCH)

    response = get(string)
    print("sending request: " + string)
    return response.content


def parse_recipe(response):
    data = loads(response.decode("utf-8"))
    instructions = ""
    ingredient_ids = []
    ingredient_names = []
    cuisines = data['results'][0]['cuisines']
    id = data['results'][0]['id']
    summary = data['results'][0]['summary']
    for inst in data['results'][0]['analyzedInstructions'][0]['steps']:
        instructions = instructions + inst['step']
        for ing in inst['ingredients']:
            if ing['id'] not in ingredient_ids:
                ingredient_ids.append(ing['id'])
                ingredient_names.append(ing['name'])

    vegetarian = data['results'][0]['vegetarian']
    vegan = data['results'][0]['vegan']
    glutenFree = data['results'][0]['glutenFree']
    dairyFree = data['results'][0]['dairyFree']

    allergyDict = {"vegan": vegan,
                   "vegetarian": vegetarian,
                   "glutenFree": glutenFree,
                   "dairyFree": dairyFree}

    return id, summary, ingredient_ids, ingredient_names, allergyDict, cuisines, instructions
