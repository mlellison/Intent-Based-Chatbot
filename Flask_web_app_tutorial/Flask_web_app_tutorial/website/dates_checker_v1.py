import pandas as pd
import numpy as np

# load datasets
vacancyHk = pd.read_csv('website/static/data/vacancyHk.csv')
listingHk = pd.read_csv('website/static/data/listingHk.csv')

vacancyHk.date = pd.to_datetime(vacancyHk.date)
print('date range:',vacancyHk.date.min(),', ', vacancyHk.date.max())

# function that returns avail listings for dates selected

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

#x = searchListing(checkIn = '2022-06-14', checkOut = '2023-06-13', numGuests = 2)