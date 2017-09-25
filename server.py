import xml.etree.ElementTree as etree 
import os
import xmltodict, json
location = os.getcwd() # get present working directory
directory = 'BILLSTATUS-115-sres'

def co_sponsor_info(bill_dict):
    sponsor_dict = bill_dict.get('billStatus').get('bill').get('cosponsors').get('item')
    sponsor_fname = sponsor_dict.get('firstName')
    sponsor_lname = sponsor_dict.get('lastName')
    sponsor_party = sponsor_dict.get('party')
    sponsor_state = sponsor_dict.get('state')
    sponsor_date = sponsor_dict.get('sponsorshipDate')
    sponsor_withdraw_date = sponsor_dict.get('sponsorshipWithdrawnDate')
    is_original_sponsor = sponsor_dict.get('isOriginalCosponsor')
    sponsor_info = {sponsor_fname + ' ' + sponsor_lname: {'original_sponsor': 
                                                         is_original_sponsor, 'state': 
                                                         sponsor_state, 'party': 
                                                         sponsor_party, 'sponsor_date': 
                                                         sponsor_date, 'withdraw_date': 
                                                         sponsor_withdraw_date }}
    return sponsor_info

def get_sponsor_info(bill_dict):
    """gets sponsor info from bill dict"""

    try: 
        sponsor_dict = bill_dict.get('billStatus').get('bill').get('sponsors').get('item')
        sponsor_fname = ((sponsor_dict.get('firstName')).lower()).capitalize()
        sponsor_lname = ((sponsor_dict.get('lastName')).lower()).capitalize()
        sponsor_party = sponsor_dict.get('party')
        sponsor_state = sponsor_dict.get('state')
        sponsor_info = {sponsor_fname + ' ' + sponsor_lname: {'state': sponsor_state, 'party': sponsor_party}}

    except KeyError:
        co_sponsor_info(bill_dict)

    finally: 
        return sponsor_info

def get_bill_info(bill_dict):
    """gets bill info from bill dict"""

    bill_info = bill_dict.get('billStatus').get('bill').get('subjects').get('billSubjects').get('legislativeSubjects').get('item')
    bill_subjects = []
    for item in bill_info:
        bill_subjects.append(item.values())


for item in os.listdir(directory):
    #opens file within the directory
    with open(directory + '/' + item,'r') as f:
        o = xmltodict.parse(f.read())
        #reads the xml file
    json_obj = json.dumps(o) 
    #converts xml to json 
    bill_dict = json.loads(json_obj)
    # converts json to dict
    sponsor_info = get_sponsor_info(bill_dict)
    print sponsor_info
    







        # for item in json_obj:

        #     if item in json_obj.keys() =='billStatus':
        #         print 'test'
        #         print item.get(u'sponsors')
        #     print item
        #     break
        # tree = etree.parse(f)
        # root = tree.getroot()

        # for item in root.iter(tag='sponsors'):
        #     print item.text
        #     for sub_item in item.iter(tag='fullName'):
        #         print sub_item.text
            
        # for element in tree.iter(tag = 'sponsors'):
        #     print element
        #     print element.tag
        # print root.tag
    
    # for node in tree.iter():
        # print node.tag, node.attrib


    break