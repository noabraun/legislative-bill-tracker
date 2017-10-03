"""Dolla Dolla Bills yo"""
""" Not fake news """

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
import wikipedia

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/bills")
def user_list():
    """Show list of bills."""

    bills = Bill.query.order_by().all()
    return render_template("bill_list.html", bills=bills)

@app.route("/bills/<bill_id>")
def bill_detail(bill_id):
    """Show info about bill."""

    bill = Bill.query.filter_by(bill_id=bill_id).first()
    return render_template("bill.html", bill=bill)

@app.route("/senators")
def senator_list():
    """Show list of senators."""

    senators = Senator.query.all()
    return render_template("senator_list.html", senators=senators)

@app.route("/senators/<name>")
def senator_detail(name):
    """Show info about senator."""

    senator_wiki = wikipedia.summary(name +" (politician)", sentences=2)
    senator = Senator.query.filter_by(name=name).first()
    return render_template("senator.html", senator=senator, 
                          senator_wiki=senator_wiki)













# @app.route("/senators/<senator.name>")
# def senator_detail(senator_id):
#     """Show info about Senator."""

#     senator = Senator.query.options(db.joinedload('ratings').joinedload('movie')).get(user_id)
#     return render_template("user.html", user=user)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
