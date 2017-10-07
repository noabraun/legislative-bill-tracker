from random import choice
import wikipedia

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
