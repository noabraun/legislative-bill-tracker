"""Dolla Dolla Bills yo"""
""" Not fake news """

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
import wikipedia
from newsapi.articles import Articles
from markupsafe import Markup
from sqlalchemy import distinct, or_


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

    bills = Bill.query.order_by(Bill.date).all()
    return render_template("bill_list.html", bills=bills)


@app.route("/bills/<bill_id>")
def bill_detail(bill_id):
    """Show info about bill."""

    bill = Bill.query.filter_by(bill_id=bill_id).first()

    sponsorship = Sponsorship.query.filter_by(bill_id=bill_id).all()
    action = Action.query.filter_by(bill_id=bill_id).order_by(Action.date).all()
    # associated_committees = BillCommittee.query.filter_by(bill_id=bill_id).all()

    # committees = []
    # for committee in associated_committees:
    #     bill_committee = Committee.query.filter_by(committee_id=committee.committee_id).first()
    #     committees.append(bill_committee)

    senators_sponsored =[]
    for item in bill.sponsorships:
        senator_id = item.senator_id
        sen_spons = Senator.query.filter_by(senator_id=senator_id).all()
        senators_sponsored.append(sen_spons)

    return render_template("bill.html", bill=bill, 
                          sponsorship=sponsorship, action=action, 
                          senators_sponsored=senators_sponsored)

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
    # image_wiki = senator_wiki_page.images
    senator_wiki = wikipedia.summary(name +" (politician)", sentences=5)
    senator = Senator.query.filter_by(name=name).first()
    bills_sponsored =[]
    for item in senator.sponsorships:
        bill_id = item.bill_id
        bill_spons = Bill.query.filter_by(bill_id=bill_id).all()
        bills_sponsored.append(bill_spons)

    return render_template("senator.html", senator=senator, 
                          senator_wiki=senator_wiki, url_wiki=url_wiki, bills_sponsored=bills_sponsored)

@app.route("/search")
def process_search_results():
    """ Use user inputted search to look for associated tags """

 # search_input = request.form.get('searchInput')

    search_input = request.args.get('nav_search')
    #returns what the user entered to search 

    search_results = {}

    senator_name = Senator.query.filter(or_(Senator.name.like("%"+search_input+"%"),
                                            Senator.state.like("%"+search_input+"%"))).all()
    search_results['senator_name'] = senator_name

    # senator_state = Senator.query.filter(Senator.state.like("%"+search_input+"%")).all()
    # search_results['senator_state'] = senator_state

    tag = Tag.query.filter(Tag.tag_text.like("%"+search_input+"%")).all()
    search_results['tag'] = tag

    committee = Committee.query.filter(Committee.name.like("%"+search_input+"%")).all()
    search_results['committee'] = committee

    action_text = Action.query.filter(Action.action_text.like("%"+search_input+"%")).all()
    search_results['action_text'] = action_text

    bill_title = Bill.query.filter(or_(Bill.title.like("%"+search_input+"%"), 
                                      Bill.description.like("%"+search_input+"%"),
                                      Bill.bill_type.like("%"+search_input+"%"))).all()
 

    search_results['bill_title'] = bill_title


    return render_template('search_results.html', search_results=search_results, search_input=search_input)


@app.route("/committees")
def committee_list():
    """Show list of committees."""

    committees = Committee.query.all()
    return render_template("committee_list.html", committees=committees)


@app.route("/committees/<name>")
def committee_detail(name):
    """Show info about committee."""
    # senator_wiki_page = wikipedia.page(name +" (politician)")
    # url_wiki = senator_wiki_page.url
    # # image_wiki = senator_wiki_page.images
    # senator_wiki = wikipedia.summary(name +" (politician)", sentences=5)
    committee = Committee.query.filter_by(name=name).first()
    bill_committee = BillCommittee.query.filter_by(committee_id=committee.committee_id).all()
    bills_sponsored =[]
    for item in bill_committee:
        bill_id = item.bill_id
        bill_spons = Bill.query.filter_by(bill_id=bill_id).all()
        bills_sponsored.append(bill_spons)

    return render_template("committee.html", committee=committee, bills_sponsored=bills_sponsored)

@app.route("/tags")
def tag_list():
    """Show list of tags."""

    tags = Tag.query.all()
    return render_template("tag_list.html", tags=tags)


@app.route("/tags/<tag_text>")
def tag_detail(tag_text):
    """Show info about tag."""

    tag = Tag.query.filter_by(tag_text=tag_text).first()
    bill_tag = BillTag.query.filter_by(tag_id=tag.tag_id).all()
    bills_tagged =[]
    for item in bill_tag:
        bill_id = item.bill_id
        bill_spons = Bill.query.filter_by(bill_id=bill_id).all()
        bills_tagged.append(bill_spons)

    return render_template("tag.html", tag=tag, bills_tagged=bills_tagged)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
