import xml.etree.ElementTree as etree 
import os
import xmltodict, json
location = os.getcwd() # get present working directory
directory = 'BILLSTATUS-115-sres'
counter = 0 
from pprint import pprint


def get_sponsor_info(bill_dict):
    """gets sponsor info from bill dict"""
    """ EDIT TRY EXCEPT """

    is_cosponsored = True if bill_dict.get('billStatus').get('bill').get('cosponsors') else False
    sponsor_info = {}
    output = open('cosponsors.json', 'a')

    if is_cosponsored:
        
        cosponsor_info = {}
        sponsor_dict = bill_dict.get('billStatus').get('bill').get('cosponsors').get('item')

        if type(sponsor_dict) == list:

            for item in sponsor_dict:
                sponsor_fname = item.get('firstName')
                sponsor_lname = item.get('lastName')
                sponsor_party = item.get('party')
                sponsor_state = item.get('state')
                sponsor_date = item.get('sponsorshipDate')
                sponsor_withdraw_date = item.get('sponsorshipWithdrawnDate')
                is_original_sponsor = item.get('isOriginalCosponsor')

                cosponsor_info = {sponsor_fname + ' ' + sponsor_lname: {'original_sponsor': 
                                                                     is_original_sponsor, 'state': 
                                                                     sponsor_state, 'party': 
                                                                     sponsor_party, 'sponsor_date': 
                                                                     sponsor_date, 'withdraw_date': 
                                                                     sponsor_withdraw_date }}
        else:
            sponsor_fname = sponsor_dict.get('firstName')
            sponsor_lname = sponsor_dict.get('lastName')
            sponsor_party = sponsor_dict.get('party')
            sponsor_state = sponsor_dict.get('state')
            sponsor_date = sponsor_dict.get('sponsorshipDate')
            sponsor_withdraw_date = sponsor_dict.get('sponsorshipWithdrawnDate')
            is_original_sponsor = sponsor_dict.get('isOriginalCosponsor')

            cosponsor_info = {sponsor_fname + ' ' + sponsor_lname: {'original_sponsor': 
                                                                 is_original_sponsor, 'state': 
                                                                 sponsor_state, 'party': 
                                                                 sponsor_party, 'sponsor_date': 
                                                                 sponsor_date, 'withdraw_date': 
                                                                 sponsor_withdraw_date }}

        json_obj = json.dumps(cosponsor_info)

        output.write(json_obj+'\n')

    else: 
        sponsor_dict = bill_dict.get('billStatus').get('bill').get('sponsors').get('item')
        sponsor_fname = ((sponsor_dict.get('firstName')).lower()).capitalize()
        sponsor_lname = ((sponsor_dict.get('lastName')).lower()).capitalize()
        sponsor_party = sponsor_dict.get('party')
        sponsor_state = sponsor_dict.get('state')
        sponsor_info = {sponsor_fname + ' ' + sponsor_lname: {'state': 
                                                             sponsor_state, 'party': 
                                                             sponsor_party}}
        return sponsor_info

    output.close()


def get_bill_info(bill_dict):
    """gets legislative Subjects and policy area from bill dict"""
    """ to be used for tags in search function """

    bill_info = bill_dict.get('billStatus').get('bill').get('subjects').get('billSubjects')
    bill_subjects = []
    for item in bill_info.get('legislativeSubjects').get('item'):
        bill_subjects.append(item.values())

    policy_area = bill_info.get('policyArea').get('name')

    return {'bill_subjects': bill_subjects, 'policy_area': policy_area}


def get_bill_title(bill_dict):

    bill_title = bill_dict.get('billStatus').get('bill').get('titles').get('item')

    if type(bill_title) == list: 
        title = bill_title[0].get('title')
    else: 
        title = bill_dict.get('billStatus').get('bill').get('titles').get('item').get('title')

    bill_title = {'bill_title': title}
    return bill_title


def get_date_introduced(bill_dict):
    date_introduced = {'date_introduced': bill_dict.get('billStatus').get('bill').get('introducedDate')}

    return date_introduced


def get_bill_type(bill_dict):
    bill_type = {'bill_type': bill_dict.get('billStatus').get('bill').get('billType')}

    return bill_type


def get_committee(bill_dict):
    committee_info = bill_dict.get('billStatus').get('bill').get('committees').get('billCommittees').get('item')
    committees = {}

    if type(committee_info) == list:
        counter = 1
        for item in committee_info: 
            committees['committee_title' + '-' + str(counter)] = item.get('name')
            counter+=1
        return committees
    else: 
        committee_info = bill_dict.get('billStatus').get('bill').get('committees').get('billCommittees').get('item').get('name')
        return {'committee_info': committee_info}


def get_bill_number(bill_dict):
    bill_number = {'bill_number': bill_dict.get('billStatus').get('bill').get('billNumber')}

    return bill_number


def get_bill_summary(bill_dict):
    bill_summary_list = bill_dict.get('billStatus').get('bill').get('summaries').get('billSummaries').get('item')
    current_summary_dict = bill_summary_list[len(bill_summary_list)-1] 
    #gets most recent summary item index

    bill_summary = current_summary_dict.get('text')
    summary_date = current_summary_dict.get('lastSummaryUpdateDate')

    return {'bill_summary': bill_summary, 'summary_date': summary_date}



for item in os.listdir(directory):
    print item
    #opens file within the directory
    with open(directory + '/' + item,'r') as f:
        counter += 1
        o = xmltodict.parse(f.read())
        #reads the xml file
    json_obj = json.dumps(o) 
    #converts xml to json 
    bill_dict = json.loads(json_obj)
    # converts json to dict
    sponsor_info = get_sponsor_info(bill_dict)
    print sponsor_info
    print counter
    

# with open(directory + '/' + 'BILLSTATUS-115sres52.xml','r') as f:
#      o = xmltodict.parse(f.read())
#         #reads the xml file
# json_obj = json.dumps(o) 
# #converts xml to json 
# bill_dict = json.loads(json_obj)
# # converts json to dict
print get_sponsor_info(bill_dict)
print get_bill_info(bill_dict)
print get_bill_title(bill_dict)
print get_date_introduced(bill_dict)
print get_bill_type(bill_dict)
print get_bill_number(bill_dict)
print get_bill_summary(bill_dict)
print get_committee(bill_dict)





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


    # break