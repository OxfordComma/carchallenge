import asyncio
from bs4 import BeautifulSoup
from itertools import chain
import datetime
import discord
import pdb
import random
import requests
import sys

lastResults = None

async def car_search_loop():
    while not client.is_closed:
        await car_search()

        #Set Sleep Here
        randtime = random.random()
        randmins = 30 + 30*randtime
        print('Sleeping for ' + str(randmins) + ' minutes.')
        await asyncio.sleep(60 * randmins) 
        
async def car_search(car=''):
    global lastResults
    
    resultsWithDupes = get_results()
    results = []
    # Remove duplicates
    for n in resultsWithDupes:
        if n['name'] not in [d['name'] for d in results]:
            results.append(n)

    results.sort(key=lambda k : datetime.datetime.strptime(k['datetime'], '%Y-%m-%d %H:%M'), reverse = False)

    narrowTo = 10
    print (str(len(results)) + ' results found.')
    print ('Narrowing down to ' + str(min(narrowTo, len(results))) + '.') 
    del results[narrowTo:]
    
    '''
    print('lastResults:' )
    if lastResults is not None:
        for result in lastResults:
            print(str(result['name']))
    print('results:')
    if results is not None:
        for result in results:
            print(str(result['name']))
    '''

    #First run
    if lastResults == None:
        print('No lastResults. Writing to Discord.')
        get_detailed_results(results[0]['url'])
        for result in results:
            desc = "{0} | {1} | {2} |<{3}>".format(result["datetime"],  result["price"], result["name"], result["url"])
            await client.send_message(channel, desc)

    elif lastResults == results:
        print('No new cars found.')
        await client.send_message(channel, 'No new cars found.')

    else:
        print('Found new results.')
        for result in results:
            if  result not in lastResults:
                #dr = get_detailed_results(result['url'])
                print(result['name'])
                desc = "{0} | {1} | {2} |<{3}>".format(
                    result["datetime"],  
                    result["price"], 
                    result["name"], 
                    result["url"])
                await client.send_message(channel, desc)

    lastResults = results

def get_results():
    url_base = 'https://boston.craigslist.org/search/cta'
    query_car = [
    'audi', 'mercedes', 'bmw', 'lexus', #luxury
    'prelude', 'si', 'crx', 'cr-x', #honda
    '240sx', '300zx', #nissan
    'cobalt', 'camaro', 'corvette', 'ss',  #chevy
    #'g5', 'g6' , 'firebird', #pontiac
    'rsx', 'integra', #acura
    'svt', 'mustang', 'sho', #ford
    'gti', #VW
    #'viggen', #saab
    'celica', 'supra', #toyota
    'impreza', 'wrx', #subaru
    'eclipse', #mitsubishi
    #'talon', #eagle?
    'miata', 'rx*' #mazda
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
        search_distance=200, 
        min_price=800, 
        max_price=1500
        )
    rsp = requests.get(url_base, params=params)
    print(rsp.raise_for_status())

    html = BeautifulSoup(rsp.text, 'html.parser')
    cars = html.find_all('p', attrs={'class':'result-info'})
    results = []
    for car in cars:
        hyperlink = car.find_all('a', attrs={'class':'result-title hdrlnk'})[0]
        name = hyperlink.text
        url = hyperlink.get('href')
        if 'craigslist.org' not in url:
            url = 'https://boston.craigslist.org' + url
        price = car.find_all('span', attrs={'class':'result-price'})[0].text
        time = car.find_all('time')[0].get('datetime')
        results.append({'name':name, 'price':price, 'url':url, 'datetime':time})

    return results

def get_detailed_results(url):
    #print('detailed results:')
    rsp = requests.get(url)
    html = BeautifulSoup(rsp.text, 'html.parser')

    model = html.find_all('p', attrs={'class':'attrgroup'})[0].find_all('b')[0].text
    text = html.find('section', attrs{'id':'postingbody'}).text
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


client = discord.Client()
channel = discord.Object(id='324377346683699200')


@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name + ' with user id ' + client.user.id)
    #await(car_search())

@client.event
async def on_message(message):
    if message.content.startswith('!challenge'):
        print('Challenge mode.')
        await car_search_loop()
    if message.content.startswith('!search'):
        await car_search()

try:
    client.run('MjMyMzEyOTk4NTIwMjkxMzI5.CtRtEw.yBBPYU6dL-pWGVH_rPF7O2Fy4io')
except ConnectionResetError:
    client.run('MjMyMzEyOTk4NTIwMjkxMzI5.CtRtEw.yBBPYU6dL-pWGVH_rPF7O2Fy4io')
    print("Unexpected error:", sys.exc_info()[0])
    raise
