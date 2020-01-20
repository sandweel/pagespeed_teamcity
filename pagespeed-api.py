#!/usr/bin/env python3.7

import os
import requests
import sys
import json

if len(sys.argv) > 1:
    build = sys.argv[1]
else:
    build = 'manual'

download_dir = 'results.csv'
results_json = 'results.json'
urls = "pagespeed_urls.txt"
file = open(download_dir, 'a+')
columnTitleRow = "Build,URL,First Contentful Paint,First Interactive\n"
file.seek(0)
csvHeader = file.readline()

if not os.path.exists(results_json):
    json_file = open(results_json, 'w+')
    json_file.write('{}')
    json_file.close()



if not columnTitleRow in csvHeader:
    file.write(columnTitleRow)

with open(results_json) as json_file:
    json_data = json.loads(json_file.read())
    json_file.close()

# Creating an empty dict
json_data[build] = {}

# Test pages and append data to json file
with open(urls) as pagespeedurls:
    content = pagespeedurls.readlines()
    content = [line.rstrip('\n') for line in content]

    # This is the google pagespeed api url structure, using for loop to insert each url in .txt file
    for line in content:
        # If no "strategy" parameter is included, the query by default returns desktop data.
        x = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={line}&strategy=desktop'
        print(f'Requesting {x}...')
        r = requests.get(x)
        final = r.json()
        try:
            urlid = final['id']
            split = urlid.split('?')  # This splits the absolute url from the api key parameter
            urlid = split[0]  # This reassigns urlid to the absolute url
            ID = f'URL ~ {urlid}'
            ID2 = str(urlid)
            urlfcp = final['lighthouseResult']['audits']['first-contentful-paint']['displayValue']
            FCP = f'First Contentful Paint ~ {str(urlfcp)}'
            FCP2 = str(urlfcp.replace(f'\xa0s', ''))
            urlfi = final['lighthouseResult']['audits']['interactive']['displayValue']
            FI = f'First Interactive ~ {str(urlfi)}'
            FI2 = str(urlfi.replace(f'\xa0s', ''))
            json_data[build][line] = {"FCP": FCP2, "FI": FI2}
        except KeyError:
            print(f'<KeyError> One or more keys not found {line}.')
        try:
            row = f'{build},{ID2},{FCP2},{FI2}\n'
            file.write(row)
        except NameError:
            print(f'<NameError> Failing because of KeyError {line}.')
            file.write(f'<KeyError> & <NameError> Failing because of nonexistant Key ~ {line}.' + '\n')
        try:
            print(ID)
            print(FCP)
            print(FI)
        except NameError:
            print(f'<NameError> Failing because of KeyError {line}.')
    file.close()

with open(results_json, "w+") as json_file:
    json_file.write(json.dumps(json_data, indent=4, sort_keys=True))

