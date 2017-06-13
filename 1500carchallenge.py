import asyncio
from bs4 import BeautifulSoup
from itertools import chain
import datetime
import discord
import pdb
import random
import requests

client = discord.Client()
channel = discord.Object(id='273260866198175745')
lastResults = None

@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name + ' with user id ' + client.user.id)
    await(car_search())

@client.event
async def on_message(message):
    if message.content.startswith('!challenge'):
        print('Challenge mode.')
        await car_search_loop()

async def car_search_loop():
    while not client.is_closed:
        await car_search()

        #Set Sleep Here
        randtime = random.random()
        print('Sleeping for ' + str(1 + randtime) + 'hours.')
        await asyncio.sleep(60 * 60 * (1 + randtime)) 
        
async def car_search(car=''):
    global lastResults
    url_base = 'https://boston.craigslist.org/search/cta'
    query_car = [
    #'audi', 'mercedes', 'bmw', 'lexus', #luxury
    #'prelude', 'si', 'crx', 'cr-x', #honda
    #'240sx', '300zx', #nissan
    #'cobalt', 'camaro', 'corvette', 'ss',  #chevy
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

    print(querystring)

    params = dict(
        query=querystring,
        bundleDuplicates=1, 
        postal='02144', 
        search_distance=200, 
        min_price=500, 
        max_price=1500
        )
    print(params)
    rsp = requests.get(url_base, params=params)
    print(rsp.raise_for_status())

    html = BeautifulSoup(rsp.text, 'html.parser')
    cars = html.find_all('p', attrs={'class':'result-info'})
    resultsWithDupes = []
    for car in cars:
        first = car.find_all('a', attrs={'class':'result-title hdrlnk'})[0]
        name = first.text
        url = first.get('href')
        price = car.find_all('span', attrs={'class':'result-price'})[0].text
        time = car.find_all('time')[0].get('datetime')
        resultsWithDupes.append({'name':name, 'price':price, 'url':url, 'datetime':time})
    
    results = []
    for n in resultsWithDupes:
        if n['name'] not in [d['name'] for d in results]:
            results.append(n)
    results.sort(key=lambda k : datetime.datetime.strptime(k['datetime'], '%Y-%m-%d %H:%M'), reverse = True)

    narrowTo = 10
    print (str(len(results)) + ' results found.')
    print ('Narrowing down to ' + str(min(narrowTo, len(results))) + '.') 
    del results[narrowTo:]
    
    print('lastResults:' )
    if lastResults is not None:
        for result in lastResults:
            print(str(result))
    print('results:')
    if results is not None:
        for result in results:
            print(str(result))

    #First run
    if lastResults == None:
        print('No lastResults. Writing to Discord.')
        for result in results:
            desc = "{0} | {1} | {2} |<{3}>".format(result["datetime"],  result["price"], result["name"], result["url"])
            await client.send_message(channel, desc)

    elif lastResults == results:
         await client.send_message(channel, 'No new cars found.')

    else:
        for result in results:
            if  result not in lastResults:
                desc = "{0} | {1} | {2} |<{3}>".format(result["datetime"],  result["price"], result["name"], result["url"])
                await client.send_message(channel, desc)
    lastResults = results


client.run('MjMyMzEyOTk4NTIwMjkxMzI5.CtRtEw.yBBPYU6dL-pWGVH_rPF7O2Fy4io')
