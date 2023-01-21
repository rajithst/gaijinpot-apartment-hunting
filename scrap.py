import requests
from bs4 import BeautifulSoup
import pandas as pd

class Property:
    def __init__(self):
        self.apartment_type = None
        self.address = None
        self.rent = None
        self.availability = None
        self.size = None
        self.deposit = None
        self.key_money = None
        self.floor = None
        self.year_built = None
        self.nearest_station = None

def split_and_merge(text,key,prop,attr=None):
    if key not in text:
        return None, None
    k1, k2 = text.split(key)
    if "¥" in k2:
        _, k2 = k2.split("¥")
    if 'apartment' in text:
        prop.__setattr__('apartment_type',k1)
        prop.__setattr__('address',k2.split("in")[1])
    else:
        if not attr:
            prop.__setattr__(key, k2)
        else:
            prop.__setattr__(attr,k2)

url = 'https://apartments.gaijinpot.com/en/rent/listing?prefecture=JP-14&city=kawasaki&district=&min_price=&max_price=&min_meter=&rooms=&distance_station=&agent_id=&building_type=&building_age=&updated_within=&transaction_type=&order=&search=Search'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
property_listing = soup.find_all("div", {"class": "property-listing"})
properties = []
for item in property_listing:
    body = item.find_all("div", {"class": "listing-body"})
    prop = Property()
    if body:
        rc = body[0].find("div", attrs={"class": "listing-right-col"})
        listing_divs = rc.select("div.listing-item")
        right_vals = []
        prop = Property()
        for dv in listing_divs:
            text = dv.get_text(strip=True).lower()
            split_and_merge(text,'apartment',prop)
            split_and_merge(text,'monthly costs',prop,'rent')
        lc = body[0].find("div", attrs={'class': 'listing-info'})
        cols = lc.find("div", attrs={'class': "listing-right-col"})
        rest_divs = cols.select("div.listing-item")
        for rdv in rest_divs:
            text = rdv.get_text(strip=True).lower()
            split_and_merge(text,'size', prop)
            split_and_merge(text,'deposit', prop)
            split_and_merge(text,'key money',prop,'key_money')
            split_and_merge(text,'floor', prop)
            split_and_merge(text,'year built',prop, 'year_built')
            split_and_merge(text,'nearest station', prop, 'nearest_station')
        properties.append(prop.__dict__)
df = pd.DataFrame.from_records(properties)
df.to_csv("apartments.csv")