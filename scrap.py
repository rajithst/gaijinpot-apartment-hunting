import requests
from bs4 import BeautifulSoup
import pandas as pd
import prefec_cities as cities
class Property:
    def __init__(self):
        self.apartment_type = None
        self.city = None
        self.address = None
        self.rent = None
        self.availability = None
        self.size = None
        self.deposit = None
        self.key_money = None
        self.floor = None
        self.year_built = None
        self.nearest_station = None
        self.link = None

def split_and_merge(text,key,prop,attr=None):
    if key not in text:
        return None, None
    k1, k2 = text.split(key)
    if "¥" in k2:
        _, k2 = k2.split("¥")
    if 'apartment' in text:
        prop.__setattr__('apartment_type',k1)
        prop.__setattr__('address',k2.split("in",1)[1])
    else:
        if not attr:
            prop.__setattr__(key, k2)
        else:
            prop.__setattr__(attr,k2)

def extraction(property_listing):
    properties = []
    for item in property_listing:
        body = item.find_all("div", {"class": "listing-body"})
        prop = Property()
        if body:
            rc = body[0].find("div", attrs={"class": "listing-right-col"})
            listing_divs = rc.select("div.listing-item")
            prop = Property()
            for dv in listing_divs:
                text = dv.get_text(strip=True).lower()
                split_and_merge(text, 'apartment', prop)
                split_and_merge(text, 'monthly costs', prop, 'rent')
            lc = body[0].find("div", attrs={'class': 'listing-info'})
            cols = lc.find("div", attrs={'class': "listing-right-col"})
            rest_divs = cols.select("div.listing-item")
            for rdv in rest_divs:
                text = rdv.get_text(strip=True).lower()
                split_and_merge(text, 'size', prop)
                split_and_merge(text, 'deposit', prop)
                split_and_merge(text, 'key money', prop, 'key_money')
                split_and_merge(text, 'floor', prop)
                split_and_merge(text, 'year built', prop, 'year_built')
                split_and_merge(text, 'nearest station', prop, 'nearest_station')
            footer = item.find_all("div", attrs={'class': 'listing-footer'})
            if footer:
                links = footer[0].find_all('a', href=True)
                if links:
                    href = links[0].attrs['href'].strip()
                    prop.__setattr__('link','https://apartments.gaijinpot.com'+href)
            properties.append(prop.__dict__)
    return properties


prefecture = 'kanagawa'
prefecture_cities = cities.kanagawa
min_price = None
max_price = None
layout_t = ['2K','2SK', '2DK', '2SLK', '2SDK', '2LDK', '2SLDK']
layout_n = [20,23,25,26,28,30,33]
layout = dict(zip(layout_t,layout_n))
results = []
for city in prefecture_cities:
    print('processing ->',city)
    for l1,l2 in layout.items():
        print('     ->',l1)
        url = 'https://apartments.gaijinpot.com/en/rent/listing?prefecture=JP-14&district=&min_price=&max_price' \
              '=&min_meter=&rooms='+ str(l2) \
              +'&distance_station=&agent_id=&building_type=&building_age=&updated_within=&transaction_type=&order' \
               '=&search=Search&city='+city
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paginator = soup.find('ul', {'class': 'paginator'})
        if not paginator:
            continue
        paginator = paginator.find_all('li')
        if len(paginator) < 3:
            continue
        paginator = paginator[3]
        from_item, to_item = paginator.get_text().strip().split('of')
        from_item, *_ = from_item.split("-")
        pages = int(to_item) // 15 + 1 if int(to_item) % 15 > 0 else 0
        for page in range(1,pages+1):
            if page != 1:
                url += '&page=' + str(page)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            property_listing = soup.find_all("div", {"class": "property-listing"})
            properties = extraction(property_listing)
            for p in properties:
                p['city'] = city
            results.extend(properties)
df = pd.DataFrame.from_records(results)
df.to_csv("kanagawa_apartments.csv", index=False)



