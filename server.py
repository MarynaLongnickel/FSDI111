from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date
from flask import Flask, jsonify, request
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Enum
)

# Create a Flask app instance
app = Flask(__name__)

# Database Setup
engine = create_engine('sqlite:///budget_manager.db') # way to connect to db
Base = declarative_base() # Base to define models, all models inhert from this
Session = sessionmaker(bind=engine) # Session factory, prepares sessions
session = Session() # Create a session instance to inteact with db (add, commit, ...)

# Define models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    expenses = relationship('Expense', back_populates='user') # user.expenses, list all

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200))
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    category = Column(Enum('Food', 'Education', 'Entertainment'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id')) # Foreign key
    user = relationship('User', back_populates='expenses') # expense.user.username

# Create tables
Base.metadata.create_all(engine)

# Health check route
@app.get('/api/health')
def health_check():
    return jsonify({"status": "ok"}), 200

# User routes
@app.post('/api/register')
def register():
    data = request.get_json()
    username = data.get('username').lower().strip()  # normalize
    password = data.get('password')

    # Validation
    existing_user = session.query(User).filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    print(data)
    print(username)
    print(password)

    new_user = User(username=username, password=password) # new User instance
    session.add(new_user)
    session.commit() # commit to DB

    return jsonify({"status": "Created"}), 201

# Login
@app.post('/api/login')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username or password missing"}), 400
    
    user = session.query(User).filter_by(username=username).first()

    if user and user.password == password:
        return jsonify({"message": "Login successful."}), 200
    else: 
        return jsonify({"message": "Wrong password."}), 401

# Get user by id
@app.get('/api/users/<user_id>')
def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user_data = {"id": user.id, "username": user.username}
    return user_data['username']

# Update user
@app.put('/api/users/<user_id>')
def update_user(user_id):
    data = request.get_json()
    new_username = data.get("username")
    new_password = data.get("password")

    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if new_username:
        user.username = new_username
        
    if new_password:
        user.password = new_password

    session.commit() # commit to DB
    return jsonify({"message": "Updated user."}), 200

# Delete user
@app.delete('/api/users/<user_id>')
def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    session.delete(user)
    session.commit() # commit to DB
    return jsonify({"message": "Deleted user."}), 200

# -----------------------------------------------------------

# Expense routes
@app.post('/api/expenses')
def add_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")
    user_id = data.get("user_id")

    # Validate category
    categories = {'food', 'education', 'entertainment'}

    if category.lower() not in categories:
        return jsonify({"error": f"Invalid category {category}"}), 400

    new_expense = Expense(title=title,
                          description=description,
                          amount=amount,
                          category=category,
                          user_id=user_id)
    session.add(new_expense)
    session.commit()

    return jsonify({"message": "Added an expense."}), 200

# Update expense
@app.put('/api/expenses/<expense_id>')
def update_expense(expense_id):
    data = request.get_json()

    expense = session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    # Update only provided fields
    if "title" in data:
        expense.title = data["title"]
    if "description" in data:
        expense.description = data["description"]
    if "amount" in data:
        expense.amount = data["amount"]
    if "category" in data:
        categories = {'food', 'education', 'entertainment'}
        if data["category"].lower() not in categories:
            return jsonify({"error": f"Invalid category {data['category']}"}), 400
        expense.category = data["category"]
    if "user_id" in data:
        expense.user_id = data["user_id"]

    session.commit()
    return jsonify({"message": "Updated expense."}), 200


# Delete expense
@app.delete('/api/expenses/<expense_id>')
def delete_expense(expense_id):
    expense = session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    session.delete(expense)
    session.commit()
    return jsonify({"message": "Deleted expense."}), 200

# Ensures the server runs ony when this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)