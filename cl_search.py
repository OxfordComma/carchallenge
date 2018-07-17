from bs4 import BeautifulSoup
import datetime
import requests
import matplotlib.pyplot as pyplot
import re
import pandas as pd
import search_constants as sc

def get_results(detailed=False):
    base_url = 'https://' + sc.location + '.craigslist.org'
    search_url = base_url + '/search/cta'
    query = sc.query
    params = sc.params

    rsp = requests.get(search_url, params=params)
    print(rsp.url)
    print(rsp.raise_for_status())

    html = BeautifulSoup(rsp.text, 'html.parser')
    cars = html.find_all('p', attrs={'class':'result-info'})
    results = []
    for car in cars:
        hyperlink = car.find_all('a', attrs={'class':'result-title hdrlnk'})[0]
        url = hyperlink.get('href')
        #if 'craigslist.org' not in url:
        #    url = 'https://boston.craigslist.org' + url
        title = hyperlink.text
        # CL returns the price with a dollar sign on the front
        price = int(car.find_all('span', attrs={'class': 'result-price'})[0].text[1:])
        time = car.find_all('time')[0].get('datetime')
        model_year = re.search('(19|20)\d{2}', title)

        if (detailed):
            rsp = requests.get(hyperlink)
            detailed_html = BeautifulSoup(rsp.text, 'html.parser')
        
            make_model_year = detailed_html.find_all('p', attrs={'class':'attrgroup'})[0].find_all('b')[0].text
            text = detailed_html.find('section', attrs={'id':'postingbody'}).text
            details = [n for n in detailed_html.find_all('p', attrs={'class':'attrgroup'})[1].get_text().split('\n') if n]
            info = {}
            info['make_model_year'] = make_model_year
            info['text'] = text
            for x in details:
                info_name = x[:x.find(':')]
                info_result = x[x.find(':')+2:]
                info[info_name] = info_result
            print(info)
            return info
            

        if model_year:
            model_year = model_year.group(0)

        results.append({'title' : title, 
                        'price' : price, 
                        'url' : url, 
                        'datetime' : time, 
                        'model_year' : model_year
                        })

    unique_results = []
    removed_results = []
    # Remove duplicates
    for n in results:
        if n['title'] not in [d['title'] for d in unique_results]:
            unique_results.append(n)
        else
            removed_results.append(n)

    unique_results.sort(key=lambda k: datetime.datetime.strptime(k['datetime'], '%Y-%m-%d %H:%M'), reverse=False)
    print('Num results:' + str(len(unique_results)))
    print('Results removed: ' + str(len(removed_results)))

    return unique_results

cars = get_results(False)
df = pd.DataFrame(cars)

groups = df.groupby('model_year')
fig, ax = pyplot.subplots()
for name, group in groups:
    ax.plot(group.model_year, group.price, marker='o', linestyle='', ms=12, label=name)
#ax.legend()

df.boxplot(column='price', by='model_year')
pyplot.show()

#df.to_csv(r'C:\users\Nick\Desktop\imprezas.csv')
df.to_csv(r'imprezas.csv')
