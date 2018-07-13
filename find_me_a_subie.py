from bs4 import BeautifulSoup
import datetime
import requests
import matplotlib.pyplot as pyplot
import re
import pandas as pd

lastResults = None

def car_search():
    global lastResults

    resultsWithDupes = get_results()
    results = []
    # Remove duplicates
    for n in resultsWithDupes:
        if n['title'] not in [d['title'] for d in results]:
            results.append(n)

    results.sort(key=lambda k : datetime.datetime.strptime(k['datetime'], '%Y-%m-%d %H:%M'), reverse = False)
    print('num results:' + str(len(results)))
    return results
    #desc = "{0} | {1} | {2} |<{3}>".format(result["datetime"],  result["price"], result["name"], result["url"])

def get_results():
    url_base = 'https://boston.craigslist.org/search/cta'
    query_car = [
        'impreza'
    ]
    query_other = ['-lease']

    querystring  = ''
    querystring += '|'.join(query_car)
    querystring += ' '
    querystring += ' '.join(query_other)

    params = dict(
        query=querystring,
        bundleDuplicates=1, 
        postal='02144', 
        search_distance=500,
        min_price=800, 
        max_price=4000
        #, auto_transmission=1
        )
    rsp = requests.get(url_base, params=params)
    print(rsp.url)
    print(rsp.raise_for_status())

    html = BeautifulSoup(rsp.text, 'html.parser')
    cars = html.find_all('p', attrs={'class':'result-info'})
    results = []
    for car in cars:
        hyperlink = car.find_all('a', attrs={'class':'result-title hdrlnk'})[0]

        title = hyperlink.text

        url = hyperlink.get('href')
        if 'craigslist.org' not in url:
            url = 'https://boston.craigslist.org' + url
        # CL returns the price with a dollar sign on the front

        price = int(car.find_all('span', attrs={'class':'result-price'})[0].text[1:])

        time = car.find_all('time')[0].get('datetime')

        model_year = re.search('(19|20)\d{2}', title)
        if model_year:
            model_year = model_year.group(0)

        results.append({'title' : title, 'price' : price, 'url' : url, 'datetime' : time, 'model_year' : model_year})

    return results

def get_detailed_results(url):
    rsp = requests.get(url)
    html = BeautifulSoup(rsp.text, 'html.parser')

    model = html.find_all('p', attrs={'class':'attrgroup'})[0].find_all('b')[0].text
    text = html.find('section', attrs={'id':'postingbody'}).text
    details = [n for n in html.find_all('p', attrs={'class':'attrgroup'})[1].get_text().split('\n') if n]
    info = {}
    info['model'] = model
    info['text'] = text
    for x in details:
        info_name = x[:x.find(':')]
        info_result = x[x.find(':')+2:]
        info[info_name] = info_result
    print(info)
    return info

cars = car_search()
df = pd.DataFrame(cars)

groups = df.groupby('model_year')
fig, ax = pyplot.subplots()
for name, group in groups:
    ax.plot(group.model_year, group.price, marker='o', linestyle='', ms=12, label=name)
#ax.legend()

df.boxplot(column='price', by='model_year')
pyplot.show()

df.to_csv(r'C:\users\nlima\Desktop\1500\imprezas.csv')
