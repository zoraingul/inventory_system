from flask import Flask, jsonify , request
from flask_cors import CORS 
import mysql.connector
from werkzeug.security import generate_password_hash , check_password_hash

app = Flask(__name__)
CORS(app)   

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='inventory_db',
    port=3307
)
cursor = db.cursor(dictionary=True)

# ----------------- REGISTER -----------------
@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')
    
    if not username or not email or not password:
        return jsonify({'error': 'Please provide all fields'}), 400

    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, role)
        )
        db.commit()
        return jsonify({'message': 'User registered successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'username or email already exists'}), 400


# ----------------- LOGIN -----------------
@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Please provide username and password'}), 400
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if check_password_hash(user['password_hash'], password):
        return jsonify({
            'message': 'Login Successful',
            'user': {
                'id': user['user_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


# ----------------- CREATE CATEGORY -----------------
@app.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category_name = data.get('category_name')
    description = data.get('description')
    created_by = data.get('created_by')
    print ("Categories Working")
    if not category_name or not created_by:
        return jsonify({'error': 'Category name and creator are required'}), 400
    
    try:
        cursor.execute(
            "INSERT INTO categories (category_name, description, created_by) VALUES (%s, %s, %s)",
            (category_name, description, created_by)
        )
        db.commit()
        return jsonify({'message': 'Category created successfully'})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    

# ----------------- GET CATEGORIES -----------------
@app.route('/categories', methods=["GET"])
def get_categories():
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    return jsonify(categories)


# ----------------- UPDATE CATEGORY -----------------
@app.route('/categories/<int:category_id>', methods=["PUT"])
def update_category(category_id):
    data = request.get_json()
    category_name = data.get('category_name')
    description = data.get('description')
    
    if not category_name and not description:
        return jsonify({'error': 'Nothing to update'}), 400

    try:
        cursor.execute(
            "UPDATE categories SET category_name=%s, description=%s WHERE category_id=%s",
            (category_name, description, category_id)
        )
        db.commit()
        return jsonify({'message': "Category updated successfully"})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500


# ----------------- DELETE CATEGORY -----------------
@app.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        db.commit()
        return jsonify({'message': 'Category Deleted Successfully'})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500


# ----------------- ADD ITEM -----------------
@app.route('/items', methods=["POST"])
def add_item():
    data = request.get_json()

    item_name = data.get('item_name')
    category_id = data.get('category_id')
    quantity = data.get('quantity')
    price = data.get('price')
    description = data.get('description')
    created_by = data.get('created_by')

    if not item_name or not category_id or quantity is None:
        return jsonify({"error": "item_name, category_id and quantity are required"}), 400        
    
    query = """
    INSERT INTO items (item_name, category_id, quantity, price, description, created_by)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (item_name, category_id, quantity, price, description, created_by)
    
    cursor.execute(query, values)
    db.commit()
    
    return jsonify({'message': 'Item added Successfully'})


# ----------------- GET ITEMS -----------------
@app.route('/items', methods=["GET"])
def get_items():
    cursor.execute("SELECT * FROM items WHERE is_deleted = 0")
    items = cursor.fetchall()
    return jsonify(items)


# ----------------- UPDATE ITEM -----------------
@app.route('/items/<int:item_id>', methods=["PUT"])
def update_item(item_id):
    data = request.get_json()

    item_name = data.get('item_name')
    category_id = data.get('category_id')
    quantity = data.get('quantity')
    price = data.get('price')
    description = data.get('description')

    fields = []
    values = []

    if item_name:
        fields.append("item_name=%s")
        values.append(item_name)
    if category_id:
        fields.append("category_id=%s")
        values.append(category_id)
    if quantity is not None:
        fields.append("quantity=%s")
        values.append(quantity)
    if price is not None:
        fields.append("price=%s")
        values.append(price)
    if description:
        fields.append("description=%s")
        values.append(description)

    if not fields:
        return jsonify({'error': 'Nothing to update'}), 400
    
    values.append(item_id)

    query = f"UPDATE items SET {', '.join(fields)} WHERE item_id=%s AND is_deleted=0"
    cursor.execute(query, values)
    db.commit()

    return jsonify({'message': 'Item updated Successfully'})


# ----------------- HOME ROUTE -----------------
@app.route('/')
def home():
    return "Backend is running successfully"


if __name__ == "__main__":
    app.run(debug=True)
