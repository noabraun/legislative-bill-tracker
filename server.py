"""Dolla Dolla Bills yo"""
""" Not fake news """

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee, Ideology
import wikipedia
from newsapi.articles import Articles
from markupsafe import Markup
from sqlalchemy import distinct, or_, desc
from helper_functions import is_empty_list, random_sad_senator, get_senator_image, calc_bill_ideology
import xmltodict, json


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
    bill_committees = BillCommittee.query.filter_by(bill_id=bill_id).all()

    committees = []
    for item in bill_committees: 
        committee_id = item.committee_id
        committee = Committee.query.filter_by(committee_id=committee_id).first()
        committees.append(committee)
    print committees

    bill_score = 0
    # senators_sponsored =[]

    for senator in bill.senators:
        # senators_sponsored.append(senator)
        ideology = Ideology.query.filter_by(senator_id=senator.senator_id).first()
        sen_ideology = ideology.score*100
        bill_score += sen_ideology

    bill_score = bill_score/(len(bill.senators))

    return render_template("bill.html", bill=bill, 
                          sponsorship=sponsorship, action=action, 
                          senators_sponsored=bill.senators, committees=committees, bill_score=bill_score)


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
    senator_id = senator.senator_id

    sen_ideology = Ideology.query.filter_by(senator_id=senator_id).first()
    progressive_score = (sen_ideology.score)*100 

    bills_sponsored =[]
    for item in senator.sponsorships:
        bill_id = item.bill_id
        bill_spons = Bill.query.filter_by(bill_id=bill_id).all()
        bills_sponsored.append(bill_spons)

    sen_image = get_senator_image(name)
    if sen_image == False: 
        sen_image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/US-Congress-UnofficialSeal.svg/2000px-US-Congress-UnofficialSeal.svg.png'

    return render_template("senator.html", senator=senator, sen_image=sen_image,
                          senator_wiki=senator_wiki, url_wiki=url_wiki, 
                          bills_sponsored=bills_sponsored, progressive_score=progressive_score)

@app.route("/search")
def process_search_results():
    """ Use user inputted search to look for associated tags """

    search_input = request.args.get('nav_search')
    #returns what the user entered to search 

    search_results = {}

    senator_name = Senator.query.filter(or_(Senator.name.like("%"+search_input+"%"),
                                            Senator.state.like("%"+search_input+"%"))).all()

    search_results['senator_name'] = senator_name

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

    if search_results.get('bill_title') == [] and search_results.get('action_text') == [] and search_results.get('committee') == [] and search_results.get('tag') == [] and search_results.get('senator_name') == []:
        #checks to see if there were no search results returned
        search_results = 'empty'

    rand_senator_image = random_sad_senator()

    return render_template('search_results.html', search_results=search_results, rand_senator_image=rand_senator_image, search_input=search_input)


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

    tags = Tag.query.order_by(Tag.tag_text).all()

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


@app.route("/senator-relationships")
def show_relationships():
    """Data Visualization of who works together"""
    relationships = {'nodes':[], 'links':[]}
    seen = set()
    nodes = []
    directory = 'static'

    for senator in Senator.query.all():
        count = {}

        if senator.party == 'D':
            group = 1
        elif senator.party == 'R': 
            group = 0
        else: 
            group = 2

        relationships.get('nodes').append({"id": senator.name, "group": group})
        #appends senator name and party group to nodes key in the final relationships dict

        bills = senator.bills #all bills sponsored by this senator

        for bill in bills: # returns each bill within the bills list
            bill_sponsors = bill.senators # each senator that has also sponsored that bill, includes current senator
            for sen in bill_sponsors:
                if sen.name == senator.name:
                    #ensure current senator wont have relationship with self
                    break
                if sen.name in seen: 
                    break
                if count.get(sen.name): 
                    count[sen.name] += 1
                else: 
                    count[sen.name] = 1
        for item in count: #item is the same as the sen values
            relationships.get('links').append({'source': senator.name, 'target': item, 'value': count.get(item)})

        # relationships.get('links').append({senator.name: count})
        seen.add(senator.name)

    output = open(directory + '/' + 'relationships.json', 'w')

    json_obj = json.dumps(relationships)
    output.write(json_obj+'\n')

    from pprint import pprint 
    pprint(relationships)


    return render_template("senator_relationships.html", relationships=relationships)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
