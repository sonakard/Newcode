
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri'
db = SQLAlchemy(app)

# Category Model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    child_categories = db.relationship('Category', backref=db.backref('parent_category', remote_side=[id]))

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'child_categories': [child_category.as_dict() for child_category in self.child_categories]
        }

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    categories = db.relationship('Category', secondary='category_product', backref='products')

# CategoryProduct Model (Many-to-Many relationship table)
category_product = db.Table('category_product',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

# API Routes
@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        categories = Category.query.filter_by(parent_category_id=None).all()
        categories_data = [category.as_dict() for category in categories]
        return jsonify(categories_data)
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        parent_category_id = data.get('parent_category_id')

        category = Category(name=name, parent_category_id=parent_category_id)
        db.session.add(category)
        db.session.commit()

        return jsonify({'message': 'Category added successfully.'})

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    category_ids = data.get('category_ids', [])

    product = Product(name=name, price=price)
    for category_id in category_ids:
        category = Category.query.get(category_id)
        if category:
            product.categories.append(category)

    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully.'})

@app.route('/categories/<category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': 'Category not found.'}), 404

    products = category.products
    products_data = [{
        'id': product.id,
        'name': product.name,
        'price': product.price
    } for product in products]

    return jsonify(products_data)

@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found.'}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    db.session.commit()

    return jsonify({'message': 'Product updated successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
