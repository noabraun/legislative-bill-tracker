"""Utility file to seed bill database from the parsed data (parse.py)"""
import datetime
from sqlalchemy import func
from model import connect_to_db, db, Bill, Senator, Committee, Tag, Action, Sponsorship, BillTag, BillCommittee
from server import app
import parse 
directory = 'BILLSTATUS-115-sres'

def load_file(directory): 
    for item in os.listdir(directory):
        if item[0] == '.':
            pass
        else: 
            #opens file within the directory
            with open(directory + '/' + item,'r') as f:
                counter += 1
                o = xmltodict.parse(f.read())
                #reads the xml file
            json_obj = json.dumps(o) 
            #converts xml to json 
            bill_dict = json.loads(json_obj)
            # converts json to dict
            
            return bill_dict
        

def load_bills():
    """Load bills from data files into database using parse.py"""

    bill_dict = load_file(directory)
    #loads bill dict from current file

    bill_number = parse.get_bill_number(bill_dict).get('bill_number')
    bill_type = parse.get_bill_type(bill_dict).get('bill_type')
    bill_title = parse.get_bill_title(bill_dict).get('bill_title')
    bill_date = parse.get_date_introduced(bill_dict).get('date_introduced')
    description = parse.get_bill_summary(bill_dict).get('bill_summary')

    date = datetime.datetime.strptime(bill_date, "%Y-%m-%d")

    bill = Bill(bill_id=bill_type + '-' + bill_number, bill_title=bill_title, 
           date=date, description=description, bill_type=bill_type)

    # adds bill to session so we can store it 
    db.session.add(bill)

    # commits bill info to DB
    db.session.commit()


def load_senators():
    """Load Senators from data files into database using parse.py"""

    print "Senators"

    bill_dict = load_file(directory)
    #loads bill dict from current file

    if parse.get_sponsor_info(bill_dict) == None: 

        with open('cosponsors.json','r') as f:
            for line in f: 
                name = line.keys()[0]
                party = line.get(name).get('party')
                original_sponsor = line.get(name).get('original_sponsor')
                state = line.get(name).get('state')

                senator = Senator(name=name, party=party, state=state, original_sponsor=original_sponsor)

                db.session.add(senator)
    else: 
        name = parse.get_sponsor_info(bill_dict).keys()[0]
        party = parse.get_sponsor_info(bill_dict).get(name).get('party')
        original_sponsor = True
        state = parse.get_sponsor_info(bill_dict).get(name).get('state')

        senator = Senator(name=name, party=party, state=state, original_sponsor=original_sponsor)

        db.session.add(senator)

    # commits bill info to DB
    db.session.commit()



def load_tags():
    """Load tags from data files into database using parse.py"""

    print "Tags"

    bill_dict = load_file(directory)
    #loads bill dict from current file

    bill_tags = parse.get_bill_info(bill_dict)

    for key in bill_tags:
        for item in bill_tags.get(key):
            tag_text = item[0]
            tag = Tag(tag_text=tag_text)

            db.session.add(tag)

    db.session.commit()


def load_committees():
    """Load committees from data files into database using parse.py"""


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_file(directory)
    load_bills()
    load_senators()
    load_tags()
    load_committees()
