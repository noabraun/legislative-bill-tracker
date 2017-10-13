"""Utility file to seed bill database from the parsed data (parse.py)"""
import datetime
import xml.etree.ElementTree as etree 
import os
import xmltodict, json
from sqlalchemy import func
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
from server import app
import parse 
from helper_functions import load_ideology
directory = 'BILLSTATUS-115-sres'
# directory = 'BILLSTATUS-115-s'
# directory = 'BILLSTATUS-115-hr'
data_directory = 'data'


def load_file(filename): 
    counter = 0 
    # for item in os.listdir(directory):
    #     if item[0] == '.':
    #         pass
    #     else: 
            #opens file within the directory
    with open(directory + '/' + filename,'r') as f:
        counter += 1
        o = xmltodict.parse(f.read())
        #reads the xml file
    json_obj = json.dumps(o) 
    #converts xml to json 
    bill_dict = json.loads(json_obj)
    # converts json to dict
    
    return bill_dict


def load_bills(bill_dict):
    """Load bills from data files into database using parse.py"""

    bill_number = str(parse.get_bill_number(bill_dict).get('bill_number'))
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    title = parse.get_bill_title(bill_dict).get('bill_title')
    bill_date = parse.get_date_introduced(bill_dict).get('date_introduced')
    description = parse.get_bill_summary(bill_dict).get('bill_summary')

    date = datetime.datetime.strptime(bill_date, "%Y-%m-%d")

    bill = Bill(bill_id=bill_type + '-' + bill_number, title=title, 
           date=date, description=description, bill_type=bill_type)

    # adds bill to session so we can store it 
    db.session.add(bill)

    # commits bill info to DB
    db.session.commit()


def load_senators(bill_dict):
    """Load Senators from data files into database using parse.py"""

    print "Senators"

    db_not_empty = Senator.query.filter_by(senator_id=1).first()


    if parse.get_sponsor_info(bill_dict) == None: 

        with open('cosponsors.json','r') as f:
            for line in f: 
                line = json.loads(line)
                name = line.keys()[0]
                party = line.get(name).get('party')
                original_sponsor = line.get(name).get('original_sponsor')
                state = line.get(name).get('state')
                name = name.title()

                senator = Senator(name=name, party=party, state=state, 
                          original_sponsor=original_sponsor)
                if not db_not_empty: #if db is empty
                    db.session.add(senator)
                elif Senator.query.filter_by(name=name).first():
                    pass
                else: 
                    db.session.add(senator)
    else: 
        name = parse.get_sponsor_info(bill_dict).keys()[0]
        party = parse.get_sponsor_info(bill_dict).get(name).get('party')
        original_sponsor = True
        state = parse.get_sponsor_info(bill_dict).get(name).get('state')
        name = name.title()
        senator = Senator(name=name, party=party, state=state, 
                  original_sponsor=original_sponsor)

        if not db_not_empty: #if db is empty
            db.session.add(senator)
        elif Senator.query.filter_by(name=name).first():
            pass
        else: 
            db.session.add(senator)

        # db.session.add(senator)

    # commits bill info to DB
    db.session.commit()

def load_ideologies():
    """Loads senator idealogies from csv and json files"""
    load_ideology()
    # populates json 
    jsonfile = open('ideology.json', 'r')

    for line in jsonfile:
        line = json.loads(line) #unjsonifies the line 
        lname = line.get('lname')

        senator = Senator.query.filter(Senator.name.like("%"+lname)).first()
        senator.ideology = line.get('ideology')

        db.session.add(senator)
    db.session.commit()

    bills = Bill.query.all()


    for bill in bills:

        bill_score = 0
        for senator in bill.senators:
            # senators_sponsored.append(senator)
            # ideology = Ideology.query.filter_by(senator_id=senator.senator_id).first()
            # ideology = senator.ideology
            sen_ideology = senator.ideology*100
            bill_score += sen_ideology

        bill_score = bill_score/(len(bill.senators))

        bill.score = bill_score
        db.session.add(bill)

    db.session.commit()

def load_tags(bill_dict):
    """Load tags from data files into database using parse.py"""

    print "Tags"

    db_not_empty = Tag.query.filter_by(tag_id=1).first()

    bill_tags = parse.get_bill_info(bill_dict)
    bill_number = parse.get_bill_number(bill_dict).get('bill_number')
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    bill_id = bill_type + '-' + bill_number

    for key in bill_tags:

        if bill_tags.get(key):
            for item in bill_tags.get(key):
                if item == None: 
                    pass
                else: 
                    tag_text = item[0]
                    tag = Tag(tag_text=tag_text)

                    if not db_not_empty: #if db is empty
                        db.session.add(tag)
                        db.session.commit()
                    elif Tag.query.filter_by(tag_text=tag_text).first():
                        pass
                    else: 
                        db.session.add(tag)
                        db.session.commit()

                    tags = Tag.query.filter_by(tag_text=tag_text).first()
                    bill_tag_item = BillTag(bill_id=bill_id, tag_id=tags.tag_id)
                    db.session.add(bill_tag_item)
                    db.session.commit() 


def load_committees(bill_dict):
    """Load committees from data files into database using parse.py"""

    print "Committees"

    db_not_empty = Committee.query.filter_by(committee_id=1).first()

    bill_number = parse.get_bill_number(bill_dict).get('bill_number')
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    bill_id = bill_type + '-' + bill_number

    for item in parse.get_committee(bill_dict).keys():
        committee_name = parse.get_committee(bill_dict).get(item)
        if committee_name == None: 
            pass
        else: 
            committee = Committee(name=committee_name)
            if not db_not_empty: #if db is empty
                    db.session.add(committee)
                    db.session.commit() 
            elif Committee.query.filter_by(name=committee_name).first():
                pass
            else: 
                db.session.add(committee) 
                db.session.commit()    
            # import pdb; pdb.set_trace()
            # committee = Committee(name=committee_name)
            # db.session.add(committee)
            # db.session.commit() 

            committees = Committee.query.filter_by(name=committee_name).first()
            bill_committee = BillCommittee(bill_id=bill_id, committee_id=committees.committee_id)
            db.session.add(bill_committee)
            db.session.commit()   

def load_actions(bill_dict):
    """Load actions from data files into database using parse.py"""

    print "Actions"

    bill_number = parse.get_bill_number(bill_dict).get('bill_number')
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    bill_id = bill_type + '-' + bill_number

    for item in parse.get_action_taken(bill_dict).get('action'):

        action_date = item[0]
        date = datetime.datetime.strptime(action_date, "%Y-%m-%d")
        action_text = item[1]

        action = Action(bill_id=bill_id, action_text=action_text, date=date)
        db.session.add(action)

    db.session.commit()

def load_sponsorships(bill_dict):
    """Load sponsorships from data files into database using parse.py"""

    print "Sponsorships"

    bill_number = parse.get_bill_number(bill_dict).get('bill_number')
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    bill_id = bill_type + '-' + bill_number

    if not parse.get_sponsor_info(bill_dict): 

        with open('cosponsors.json','r') as f:
            for line in f: 

                line = json.loads(line)
                name = line.keys()[0]
                #fix capitaliztion and redundancy in senator table
                date = line.get(name).get('withdraw_date')
                name = name.title()
                senator = Senator.query.filter_by(name=name).first()

                if not date: 
                    withdrawn = False
                    withdrawn_date = None
                else:
                    withdrawn_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    withdrawn = True

                sponsorship = Sponsorship(bill_id=bill_id, senator=senator, 
                              withdrawn=withdrawn, withdrawn_date=withdrawn_date)

                db.session.add(sponsorship)
                db.session.commit()

    else: 
        withdrawn = False
        withdrawn_date = None

        name = parse.get_sponsor_info(bill_dict).keys()[0]

        senator = Senator.query.filter_by(name=name).first()

        sponsorship = Sponsorship(bill_id=bill_id, senator=senator, 
                      withdrawn=withdrawn, withdrawn_date=withdrawn_date)

        db.session.add(sponsorship)
        db.session.commit()

    # db.session.commit()
    

    

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    # for type_directory in os.listdir(data_directory):
    for item in os.listdir(directory):
        if item[0] == '.':
            pass
        else: 
            bill_dict = load_file(item)
            load_bills(bill_dict)
            load_senators(bill_dict)
            load_tags(bill_dict)
            load_committees(bill_dict)
            load_actions(bill_dict)
            load_sponsorships(bill_dict)
    load_ideologies()


