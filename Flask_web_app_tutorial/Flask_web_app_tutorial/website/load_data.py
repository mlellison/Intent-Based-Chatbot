import xdrlib
import pandas as pd

x= str([767022, 304876, 1300549, 1370155, 1435069, 1443229, 1576511, 991336 ])

x=1


def Convert(string):
    x = list(string.split(" "))
    return x


def load_df(x):
    data = pd.read_csv("static\data\listingHk.csv")
    if 'x' in locals():
        data=data[data['id'].isin(x)]
    else:
        data=data[data['id'].isin([767022,1253977])]
    data = pd.DataFrame(data, columns = ['latitude','longitude','host_name', 'id'])
    data.head()
    return data

#data = pd.read_csv("static\data\listingHk.csv")
data=load_df(x)
print(data.head())
print(x)