from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date
from flask import Flask
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
    user = relationship('User', back_populates='expense') # expense.user.username

# Create tables
Base.metadata.create_all(engine)

# Ensures the server runs ony when this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)