# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import pandas as pd
import numpy as np
import spacy
import math
import ast
from gensim.matutils import cossim

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# import csv
#listingHk = pd.read_csv("listingHk.csv")
listingHk = pd.read_csv("listingHk.csv")
vacancyHk = pd.read_csv("vacancyHk.csv")
topics = pd.read_csv('listingTopics.csv')

# convert to datetime
vacancyHk.date = pd.to_datetime(vacancyHk.date)
topics.set_index('id', inplace=True)


# Suggestion begin
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_suggestion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        input_checkin_date = tracker.get_slot("checkin_date")
        input_checkout_date = tracker.get_slot("checkout_date")
        input_guest_number = [int(tracker.get_slot('num_guest'))]

        def searchListing(checkIn = '2022-06-14', checkOut = '2023-06-13', numGuests = 2):
            # convert dates to datetime and get length of stay
            checkIn, checkOut = pd.to_datetime(checkIn), pd.to_datetime(checkOut)
            stayLen = int((checkOut - checkIn) / np.timedelta64(1, 'D'))
            
            # return listings that match chosen period of stay
            dfStay = vacancyHk.query('minimum_nights >= @stayLen <= maximum_nights').query('date >= @checkIn and date < @checkOut') 
            dfList = dfStay.groupby('listing_id').date.count()
            availListing = [dfList.index[i] for i in range(len(dfList)) if dfList.values[i] == stayLen]
            
            # return listings that match number of guests, period of stay
            return [listing for listing in availListing 
                    if listingHk[listingHk.id == listing].accommodates.values[0] >= numGuests]
        
        global roomIdList

        # roomIdList is the room id list matched user's requirement
        roomIdList = searchListing(input_checkin_date, input_checkout_date, input_guest_number)
        # filter listingHk dataframe with roomIdList
        roomIdDF = listingHk[listingHk['id'].isin(roomIdList)]

        buttons = []
        myelements=[]

        for index, row in roomIdDF.iterrows():
            
            payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
        
            newobj={
                    "title": row['nameEn'],
                    "subtitle": row['price'],
                    "image_url": row['picture_url'],
                    "buttons": [
                        {
                        "title": "Book now",
                        "url": row['listing_url'],
                        "type": "web_url"
                        }, 
                        {
                        "title": "Details",
                        "type": "postback",
                        "payload":payload
                        },
                    ]
                }
            myelements.append(newobj)
        message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": myelements
                        
                        }
                    }

       
        dispatcher.utter_message(attachment=message)

        return []

# View more
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_room"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            clicked_room_id = [int(tracker.get_slot('room_id'))]

            ls = listingHk.loc[listingHk['id'].isin(clicked_room_id)]
            buttons = []
            myelements=[]

            for index, row in ls.iterrows():

                dispatcher.utter_message(text = row['nameEn'])
                dispatcher.utter_message(text = row['field1'])
                dispatcher.utter_message(text = row['field2'])
                dispatcher.utter_message(text = row['field3'])
            
                payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
                payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
                payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
                payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
                payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
            
                newobj={
                        "title": row['nameEn'],
                        "subtitle": row['price'],
                        "image_url": row['picture_url'],
                        "buttons": [
                            {
                            "title": "Book now",
                            "url": row['listing_url'],
                            "type": "web_url"
                            },  
                            {
                            "title": "Similar Price",
                            "type": "postback",
                            "payload":payload_price
                            },
                            {
                            "title": "Similar Amenities",
                            "type": "postback",
                            "payload":payload_amenities
                            },
                            {
                            "title": "Similar Descriptions",
                            "type": "postback",
                            "payload":payload_listing
                            },
                            {
                            "title": "Similar Location",
                            "type": "postback",
                            "payload":payload_location
                            },
                        ]
                    }
                myelements.append(newobj)
                message = {
                            "type": "template",
                            "payload": {
                                "template_type": "generic",
                                "elements": myelements
                                
                                }
                            }

        
                dispatcher.utter_message(attachment=message)

                dispatcher.utter_message(text = "Type 'return' to see your first search, or refresh page to begin a new one")
            
            return []

# Similar price
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_room_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        def filterPrice(listingId):
            # create df of primary search listings, organized by price bins
            df = pd.qcut(pd.to_numeric(
                listingHk[listingHk.id.isin(roomIdList)].price.str.replace(',','', regex=False).str.replace('$','', regex=False)),
                        [0, 0.25, 0.5, 0.75, 1]).to_frame()
            # df['id'] = roomIdList
            df['id'] = listingHk[listingHk.id.isin(roomIdList)].id.to_list()

            # return list of ten listings matching price bin of selected listing
            return df[df.price == df[df.id == listingId].price.values[0]].id.to_list()[1:]

        clicked_room_id = int(tracker.get_slot('room_id'))
        similarPriceRoomIdList = filterPrice(clicked_room_id)
        
        ls = listingHk[listingHk['id'].isin(similarPriceRoomIdList)]

        buttons = []
        myelements=[]
        for index, row in ls.iterrows():
            
            payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
        
            newobj={
                    "title": row['nameEn'],
                    "subtitle": row['price'],
                    "image_url": row['picture_url'],
                    "buttons": [
                        {
                        "title": "Book now",
                        "url": row['listing_url'],
                        "type": "web_url"
                        },  
                        {
                        "title": "Details",
                        "type": "postback",
                        "payload":payload
                        },
                    ]
                }
            myelements.append(newobj)
        message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": myelements
                        
                        }
                    }

       
        dispatcher.utter_message(attachment=message)
        dispatcher.utter_message(text = "Type 'return' to see your first search, or refresh page to begin a new one")

        return []

# Similar Amenities
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_room_amenities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        import en_core_web_lg

        nlp = en_core_web_lg.load()

        from spacy.tokens import DocBin

        # Deserialize spacy file containing all amenities word embeddings
        doc_bin = DocBin().from_disk('amenities.spacy')
        docs = list(doc_bin.get_docs(nlp.vocab))

        # Loading spacy text into dict values with listing_ids as key
        dictListing = dict()
        for idx in range(len(listingHk)):
            dictListing[listingHk.id[idx]] = docs[idx]

        # function to filter for listings with similar amenties

        def filterAmenities(listingId):
            dictScore = dict()
            
            # calculate similarity scores of selected listing and all listings
            for listing in roomIdList:#dictListing.keys():
                dictScore[listing] = dictListing[listingId].similarity(dictListing[listing])

            # return up to top ten listing matches with similar amenities
            return [key for key in dict(sorted(dictScore.items(), key=lambda item: item[1], reverse = True)).keys()][1:11]

        clicked_room_id = int(tracker.get_slot('room_id'))

        similarAmenitiesRoomIdList = filterAmenities(clicked_room_id)

        ls = listingHk[listingHk['id'].isin(similarAmenitiesRoomIdList)]

        buttons = []
        myelements=[]

        for index, row in ls.iterrows():
            
            payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
        
            newobj={
                    "title": row['nameEn'],
                    "subtitle": row['price'],
                    "image_url": row['picture_url'],
                    "buttons": [
                        {
                        "title": "Book now",
                        "url": row['listing_url'],
                        "type": "web_url"
                        },  
                        {
                        "title": "Details",
                        "type": "postback",
                        "payload":payload
                        },
                    ]
                }
            myelements.append(newobj)
        message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": myelements
                        
                        }
                    }

       
        dispatcher.utter_message(attachment=message)
        dispatcher.utter_message(text = "Type 'return' to see your first search, or refresh page to begin a new one")

        return []

# Similar Descriptions
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_room_listing"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # function to filter for listings with similar descriptors

        def filterDesc(listingId):
            dictScore = dict()
            
            # calculate similarity scores of selected listing and all listings
            for listing in roomIdList:#dictListing.keys():
                dictScore[listing] = cossim(dict([tuple(el.value for el in i.elts) for i in ast.parse(topics.topics[listingId]).body[0].value.elts]), 
                                            dict([tuple(el.value for el in i.elts) for i in ast.parse(topics.topics[listing]).body[0].value.elts]))

            # return up to top ten listing matches with similar amenities
            return [key for key in dict(sorted(dictScore.items(), key=lambda item: item[1], reverse = True)).keys()][1:11]

        clicked_room_id = int(tracker.get_slot('room_id'))
        similarListingRoomIdList = filterDesc(clicked_room_id)
        
        ls = listingHk[listingHk['id'].isin(similarListingRoomIdList)]

        buttons = []
        myelements=[]
        for index, row in ls.iterrows():
            
            payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
        
            newobj={
                    "title": row['nameEn'],
                    "subtitle": row['price'],
                    "image_url": row['picture_url'],
                    "buttons": [
                        {
                        "title": "Book now",
                        "url": row['listing_url'],
                        "type": "web_url"
                        },  
                        {
                        "title": "Details",
                        "type": "postback",
                        "payload":payload
                        },
                    ]
                }
            myelements.append(newobj)
        message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": myelements
                        
                        }
                    }

       
        dispatcher.utter_message(attachment=message)
        dispatcher.utter_message(text = "Type 'return' to see your first search, or refresh page to begin a new one")

        return []

# Similar Location
class ActionGetSuggestion(Action):

    def name(self) -> Text:
        return "action_get_room_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # function to filter for listings with similar descriptors

        # function to rank listings by distance

        def filterDistance(listingId):
            df = pd.DataFrame(listingHk[listingHk.id.isin(roomIdList)].id.to_list(), columns=['id'])
            df['distance'] = [
            math.dist(
                (listingHk[listingHk.id == listingId].longitude.to_list()[0], 
                listingHk[listingHk.id == listingId].latitude.to_list()[0]), 
                (listingHk[listingHk.id.isin(roomIdList)].longitude.to_list()[i], 
                listingHk[listingHk.id.isin(roomIdList)].latitude.to_list()[i])
                ) for i in range(len(df))]
            df.sort_values(by='distance', inplace=True)
            return df.id.to_list()[1:]  # return nearest listings other than self

        clicked_room_id = int(tracker.get_slot('room_id'))
        similarLocationRoomIdList = filterDistance(clicked_room_id)
        
        ls = listingHk[listingHk['id'].isin(similarLocationRoomIdList)]

        buttons = []
        myelements=[]
        for index, row in ls.iterrows():
            
            payload = "/room{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_price = "/room_price{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_amenities = "/room_amenities{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_listing = "/room_listing{\"room_id\":\"" + str(row['id']) + "\"}"
            payload_location = "/room_location{\"room_id\":\"" + str(row['id']) + "\"}"
        
            newobj={
                    "title": row['nameEn'],
                    "subtitle": row['price'],
                    "image_url": row['picture_url'],
                    "buttons": [
                        {
                        "title": "Book now",
                        "url": row['listing_url'],
                        "type": "web_url"
                        },  
                        {
                        "title": "Details",
                        "type": "postback",
                        "payload":payload
                        },
                    ]
                }
            myelements.append(newobj)
        message = {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": myelements
                        
                        }
                    }

       
        dispatcher.utter_message(attachment=message)
        dispatcher.utter_message(text = "Type 'return' to see your first search, or refresh page to begin a new one")
        
        return []