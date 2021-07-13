import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    home = mongo.db.actors.find()
    recent = list(mongo.db.actors.find().sort("date", -1))
    return render_template("home.html", home=home, recent=recent)


@app.route("/actors")
def actors():
    actors = mongo.db.actors.find()
    return render_template("search.html", actors=actors)


@app.route("/actors/<actor_id>")
def actor(actor_id):
    actor = mongo.db.actors.find_one({"_id": ObjectId(actor_id)})
    return render_template("actors.html", actors=actors)


# Search functionality
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    actors = (mongo.db.actors.find({"$text": {"$search": query}}))
    return render_template("search.html", actors=actors)


# Signup functionality created by following Code Institute's video
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))
        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("signup.html")


# Login functionality
@app.route("/login")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("home"))
            else:
                # invalid password match
                flash("Incorrect User and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect User and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


# Logout functionality
@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have succesfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Add actor functionality
@app.route("/actors/add", methods=["GET", "POST"])
def add_actors():
    if request.method == "POST":
        actor = {
            "full_name": request.form.get("full_name"),
            "nationality": request.form.get("nationality"),
            "dob": request.form.get("dob"),
            "favourite_movie": request.form.get("favourite_movie"),
            # "description": request.form.get("description"),
            "oscars": request.form.get("oscars"),
            "filmography": request.form.get("filmography"),
            "added_by": session["user"],
            "date": datetime.datetime.utcnow()
        }
        mongo.db.actors.insert_one(actor)
        flash("An Actor was Succesfully Added")
        return redirect(url_for("actors"))
    return render_template("add_actors.html")


# Edit actor functionality
@app.route("/edit_actors/<actors_id>", methods=["GET", "POST"])
def edit_actors(actors_id):
    if request.method == "POST":
        submit = {
            "full_name": request.form.get("full_name"),
            "nationality": request.form.get("nationality"),
            "dob": request.form.get("dob"),
            "favourite_movie": request.form.get("favourite_movie"),
            "oscars": request.form.get("oscars"),
            "filmography": request.form.get("filmography")
        }
        mongo.db.actors.update({"_id": ObjectId(actors_id)}, submit)
        flash("An Actor was updated")
        return redirect(url_for("actors"))

    actor = mongo.db.actors.find_one({"_id": ObjectId(actors_id)})
    return render_template("edit_actors.html", actor=actor)


# Delete actor functionality
@app.route("/delete_actor/<actor_id>")
def delete_actor(actor_id):
    mongo.db.actors.remove({"_id": ObjectId(actor_id)})
    flash("Actor was deleted")
    return redirect(url_for("actors"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
