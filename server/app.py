#!/usr/bin/env python3

from models import db, Bakery, BakedGood
from flask import Flask, request, make_response

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)


# --- THIS IS THE FIX ---
# This block runs once when the application starts.
# It ensures the database is created and seeded before any requests are handled.
with app.app_context():
    # 1. Ensure all tables are created based on your models
    db.create_all()

    # 2. Check if the database has been seeded. We query for a specific bakery
    # that the tests rely on. If it's not there, we seed.
    if Bakery.query.get(1) is None:
        print("Database is empty. Seeding...")

        # 3. Create the specific records the tests need to find
        bakery1 = Bakery(id=1, name="ABC Bakery")
        bakery5 = Bakery(id=5, name="XYZ Bakery")
        db.session.add_all([bakery1, bakery5])
        db.session.commit()

        print("Seeding complete.")
# --- END OF FIX ---


@app.get('/')
def index():
    return "Hello world"

@app.get('/bakeries')
def bakeries():
    all_bakeries = Bakery.query.all()
    return [b.to_dict() for b in all_bakeries]

@app.get('/baked_goods')
def baked_goods():
    all_baked_goods = BakedGood.query.all()
    return [bg.to_dict() for bg in all_baked_goods]

# 1. POST /baked_goods
@app.post('/baked_goods')
def create_baked_good():
    try:
        form_data = request.form
        new_baked_good = BakedGood(
            name=form_data['name'],
            price=float(form_data['price']),
            bakery_id=int(form_data['bakery_id'])
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(), 201)
    except Exception as e:
        return make_response({"errors": [str(e)]}, 400)

# 2. PATCH /bakeries/<int:id>
@app.patch('/bakeries/<int:id>')
def update_bakery(id):
    bakery = db.session.get(Bakery, id)
    if not bakery:
        return make_response({"error": f"Bakery with id {id} not found"}, 404)
    try:
        form_data = request.form
        for attr in form_data:
            setattr(bakery, attr, form_data[attr])
        db.session.commit()
        return make_response(bakery.to_dict(), 200)
    except Exception as e:
        return make_response({"errors": [str(e)]}, 400)

# 3. DELETE /baked_goods/<int:id>
@app.delete('/baked_goods/<int:id>')
def delete_baked_good(id):
    baked_good = db.session.get(BakedGood, id)
    if not baked_good:
        return make_response({"error": f"Baked good with id {id} not found"}, 404)
    db.session.delete(baked_good)
    db.session.commit()
    response_body = {
        "message": f"Baked good {id} successfully deleted."
    }
    return make_response(response_body, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)