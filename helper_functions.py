from random import choice
import wikipedia
import csv
import json
import plotly

def is_empty_list(input_list):
    if input_list == []:
        return True
    else:
        return False


def random_sad_senator(): 
    sad_senators = ['http://i.huffpost.com/gen/1234592/images/o-MITCH-MCCONNELL-facebook.jpg',
                   'https://bloximages.newyork1.vip.townnews.com/postandcourier.com/content/tncms/assets/v3/editorial/0/f0/0f0da79c-e41e-11e6-8201-97f15835cab4/58063b8b5d51f.image.jpg?resize=1200%2C800',
                   'http://i.huffpost.com/gen/5043460/images/o-JEFF-SESSIONS-SENATE-facebook.jpg',
                   'https://josephkaminski.org/wp-content/uploads/2016/05/sad-ted-cruz.jpg',
                   'http://thehill.com/sites/default/files/cassidybill_grahamlindsey_091317gn_lead.jpg',
                   'http://i.huffpost.com/gen/1448414/images/o-RON-JOHNSON-facebook.jpg']
    return choice(sad_senators)


def get_senator_image(name):
    last_name = name.split()
    last_name = last_name[1]
    senator_images = wikipedia.page('Current_members_of_the_United_States_Senate')
    image_wiki = senator_images.images

    print last_name

    for item in image_wiki: 

        index = item.find(last_name)

        if index != -1: 
            senator_image = item
            return senator_image
        else: 
            pass


def load_ideology():
    csvfile = open('political_leaning.csv', 'r')
    jsonfile = open('ideology.json', 'w')

    fieldnames = ("ideology","lname")
    reader = csv.DictReader( csvfile, fieldnames)
    for row in reader:
        json.dump(row, jsonfile)
        jsonfile.write('\n')


def calc_bill_ideology(senator_list):
    bill_score = 1
    for senator in senator_list: 
        sen_id = senator.senator_id
        ideology = Ideology.query.filter_by(senator_id=sen_id)
        sen_ideology = ideology.score
        bill_score *= sen_ideology
    return sen_ideology

y_axis = {'0-20':0, '21-40':0, '41-60':0, '61-80':0, '81-100':0}

def create_bar_graph(bill_spons):

    if len(bill_spons) == 1: 
        bill_spons = [bill_spons]

    for item in bill_spons:

        for thing in item: 


            if thing.score >= 0 and thing.score <=20:
                y_axis['0-20'] = y_axis.get('0-20')+1
                # print y_axis.get('0-20')+1

            elif thing.score >= 21 and thing.score <=40:
                y_axis['21-40'] = y_axis.get('21-40')+1
                # print y_axis.get('21-40')+1

            elif thing.score >= 41 and thing.score <=60:
                y_axis['41-60'] = y_axis.get('41-60')+1
                # print y_axis.get('41-60')+1

            elif thing.score >= 61 and thing.score <=80:
                y_axis['61-80'] = y_axis.get('61-80')+1
                # print y_axis.get('61-80')+1

            elif thing.score >= 81 and thing.score <=100:
                y_axis['81-100'] = y_axis.get('81-100')+1
                # print y_axis.get('81-100')+1

    return y_axis



















