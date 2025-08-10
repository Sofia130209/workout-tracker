import os

from flask import Flask, render_template, request, redirect, url_for, session

from dotenv import load_dotenv

from moduls.models import db, Exercises, Users

from moduls.my_csv import to_csv

load_dotenv()

#! СОЗДАНИЕ ПРИЛОЖЕНИЯ
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)  # * инициализация бд


# TODO : руты сайта
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return (
                render_template("login.html", error="Все поля должны быть заполнены!"),
                400,
            )

        user = Users.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["username"] = username
            session["user_id"] = user.id
            session["logged_in"] = True

            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        all_usernames = Users.query.all()
        if username in all_usernames:
            return (
                render_template(
                    "register.html",
                    error="Такое имя пользователя уже существует, придумайте другое",
                ),
                400,
            )

        if not username:
            return (
                render_template(
                    "register.html", error="Имя пользователя не должно быть пустым"
                ),
                400,
            )

        try:
            username = str(username)
        except ValueError:
            return (
                render_template(
                    "register.html", error="Логин должен содержать в себе только буквы"
                ),
                400,
            )

        # * создаём пользователя
        user = Users(username=username)
        user.set_password(password=password)

        session["user_id"] = user.id

        # * записываем в бд
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    all_data = (
        db.session.query(Exercises)
        .join(Users, Exercises.user_id == Users.id)
        .filter(Users.username == session.get("username"))
        .all()
    )

    data = [{"exercise": i.exercise, "amount": i.amount} for i in all_data]

    return (
        render_template("index.html", data=data, username=session.get("username")),
        200,
    )


@app.route("/add-workout", methods=["GET", "POST"])
def add_workout():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = request.form.get(
            "amount"
        )  # * получение значения из html-формы по аттрибуту name
        exercise = request.form.get(
            "exercise"
        )  # * получение значения из html-формы по аттрибуту name

        # * проверка корректности amount
        if not amount:
            return (
                render_template("add_workout.html", error="Значение не указано!"),
                400,
            )

        try:
            amount = int(amount)
        except ValueError:
            return (
                render_template("add_workout.html", error="Неверный формат значения!"),
                400,
            )

        if amount < 0:
            return (
                render_template(
                    "add_workout.html", error="Значение не может быть отрицательным!"
                ),
                400,
            )

        # * проверка корректности exercise
        if not exercise:
            return (
                render_template("add_workout.html", error="Название не указано!"),
                400,
            )

        try:
            exercise = str(exercise)
        except ValueError:
            return (
                render_template(
                    "add_workout.html", error="Название должно быть записано буквами!"
                ),
                400,
            )

        user = Users.query.filter_by(username=session.get("username")).first()
        if not user:
            return redirect(url_for("login"))

        # * записываем в бд
        new_exercise = Exercises(exercise=exercise, amount=amount, user_id=user.id)
        db.session.add(new_exercise)
        db.session.commit()

        # * запись в csv
        to_csv(user_id=user.id, exercise=exercise, amount=amount)

        return redirect(url_for("index"))

    return render_template("add_workout.html")


#! ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == "__main__":
    # * создание таблиц базы данных
    with app.app_context():
        # db.drop_all()  # * удаляет все таблицы
        db.create_all()  # * создаёт все таблицы

    # * запуск приложения
    app.run(debug=True)
