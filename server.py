"""Dolla Dolla Bills yo"""
""" Not fake news """

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, Markup
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
import wikipedia
from newsapi.articles import Articles
from markupsafe import Markup
from sqlalchemy import distinct, or_, desc
from helper_functions import is_empty_list, random_sad_senator, get_senator_image, calc_bill_ideology, create_bar_graph
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

    num_bills = len(Bill.query.all())

    if num_bills % 20 != 0: 
        max_pages = (num_bills/20) + 1
    else:
        max_pages = (num_bills/20)

    page_num = int(request.args.get('page', 1))
    offset = (page_num-1)*20

    bills = Bill.query.order_by(Bill.date).limit(20).offset(offset).all()

    return render_template("bill_list.html", bills=bills, page_num=page_num, num_bills=num_bills, max_pages=max_pages)


@app.route("/bills/<bill_id>")
def bill_detail(bill_id):
    """Show info about bill."""

    bill = Bill.query.filter_by(bill_id=bill_id).first()

    sponsorship = Sponsorship.query.filter_by(bill_id=bill_id).all()
    action = Action.query.filter_by(bill_id=bill_id).order_by(Action.date, Action.action_text).all()

    if len(action) > 4: 
        timeline_approved = True
    else: 
        timeline_approved = False

    bill_committees = BillCommittee.query.filter_by(bill_id=bill_id).all()

    committees = []
    for item in bill_committees: 
        committee_id = item.committee_id
        committee = Committee.query.filter_by(committee_id=committee_id).first()
        committees.append(committee)
    print committees

    bill_score = bill.score

    return render_template("bill.html", bill=bill, 
                          sponsorship=sponsorship, action=action, 
                          senators_sponsored=bill.senators, committees=committees, 
                          bill_score=bill_score, timeline_approved=timeline_approved)


@app.route("/senators")
def senator_list():
    """Show list of senators."""

    senators = Senator.query.order_by(Senator.state).all()

    return render_template("senator_list.html", senators=senators)


@app.route("/senators/<name>")
def senator_detail(name):
    """Show info about senator."""
    senator_wiki_page = wikipedia.page(name +" (politician)")
    url_wiki = senator_wiki_page.url
    senator_wiki = wikipedia.summary(name +" (politician)", sentences=5)

    senator = Senator.query.filter_by(name=name).first()
    senator_id = senator.senator_id

    progressive_score = (senator.ideology)*100 

    bills_sponsored =[]


    for item in senator.sponsorships:
        bill_id = item.bill_id
        bill_spons = Bill.query.filter_by(bill_id=bill_id).all()
        bills_sponsored.append(bill_spons)

    y_axis = create_bar_graph(bills_sponsored)

    sen_image = get_senator_image(name)
    if sen_image == None: 
        sen_image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/US-Congress-UnofficialSeal.svg/2000px-US-Congress-UnofficialSeal.svg.png'

    return render_template("senator.html", senator=senator, sen_image=sen_image,
                          senator_wiki=senator_wiki, url_wiki=url_wiki, 
                          bills_sponsored=bills_sponsored, progressive_score=progressive_score, y_axis=y_axis)

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

    num_tags = len(Tag.query.all())
    if num_tags % 20 != 0: 
        max_pages = (num_tags/20) + 1
    else:
        max_pages = (num_tags/20)

    page_num = int(request.args.get('page', 1))
    offset = (page_num-1)*20

    tags = Tag.query.order_by(Tag.tag_text).limit(20).offset(offset).all()

    return render_template("tag_list.html", tags=tags, page_num=page_num, num_tags=num_tags, max_pages=max_pages)


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


@app.route('/pick-relationships', methods=['GET'])
def process_form():
    """Show senator_relationships form."""

    senators = Senator.query.all()

    return render_template("pick_relationships.html", senators=senators)



@app.route('/senator-relationships', methods=['POST'])
def show_relationships():
    """Data Visualization of who works together"""
    relationships = {'nodes':[], 'links':[]}
    seen = set()
    nodes = []
    directory = 'static'

    senators = request.form.getlist('senators')

    for senator in senators:
        senator = Senator.query.filter_by(name=senator).first()
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
                    continue
                if sen.name in seen or sen.name not in senators: 
                    continue
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
    print relationships

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
