from app import app, db
from app.models import User, Offer, Order

user1 = User(
    username = 'mark',
    email = 'mswaringen@gmail.com',
    first_name = 'Mark',
    last_name = 'Swaringen',
    country = 'Singapore'
)
user1.set_password('pass')
db.session.add(user1)
db.session.commit()

user2 = User(
    username = 'susan',
    email = 'susan@example.com',
    first_name = 'Susan',
    last_name = 'Example',
    country = 'Mexico'
)
user2.set_password('pass')
db.session.add(user2)
db.session.commit()

offer = Offer(
    title = 'Pizza',
    body = '4 cheeze',
    servings = '6',
    expiration = 'tomorrow',
    category_id = '5',
    condition = "fresh",
    author = user1)
db.session.add(offer)
db.session.commit()

order = Order(
    user_id = 2,
    offer_id = 1
)
db.session.add(order)
db.session.commit()

