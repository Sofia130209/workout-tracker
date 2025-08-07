from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Exercises(db.Model):
    __tablename__ = "Exercises"

    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(50), unique=False, nullable=False)
    amount = db.Column(db.Integer, unique=False, nullable=False)

    @validates("amount")
    def validate_value(self, key, value):
        if value < 0:
            raise ValueError("Значение не может быть отрицательным")
        return value

    def __repr__(self):
        return f"<Exercise {self.exercise}, amount {self.amount}>"


class Users(db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=20
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"
