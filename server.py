"""Dolla Dolla Bills yo"""
""" Not fake news """

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
import wikipedia
from newsapi.articles import Articles
from markupsafe import Markup


a = Articles(API_KEY="336f09646bd34a7b9736a784bb20abe4")

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
def bill_list():
    """Show list of bills."""

    bills = Bill.query.order_by().all()
    return render_template("bill_list.html", bills=bills)

@app.route("/bills/<bill_id>")
def bill_detail(bill_id):
    """Show info about bill."""

    bill = Bill.query.filter_by(bill_id=bill_id).first()

    sponsorship = Sponsorship.query.filter_by(bill_id=bill_id).all()
    action = Action.query.filter_by(bill_id=bill_id).all()

    return render_template("bill.html", bill=bill, 
                          sponsorship=sponsorship, action=action)


@app.route("/senators")
def senator_list():
    """Show list of senators."""

    senators = Senator.query.all()
    return render_template("senator_list.html", senators=senators)

@app.route("/senators/<name>")
def senator_detail(name):
    """Show info about senator."""
    senator_wiki_page = wikipedia.page(name +" (politician)")
    url_wiki = senator_wiki_page.url
    senator_wiki = wikipedia.summary(name +" (politician)", sentences=5)
    senator = Senator.query.filter_by(name=name).first()
    return render_template("senator.html", senator=senator, 
                          senator_wiki=senator_wiki, url_wiki=url_wiki)














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
