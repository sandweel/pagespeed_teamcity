#!/usr/bin/env python3.7

import requests
import sys
from slack_webhook import Slack
import csv
import json

if len(sys.argv) > 1:
    build = sys.argv[1]
else:
    build = 'manual'


def sendMessage(message):
    slack = Slack(url='https://hooks.slack.com/services/###')  # Slack webhook
    slack.post(
               attachments=[{
                   "color": "#ff0000",
                   #"fallback": "Plan a vacation",
                   "author_name": "",
                   "title": "Speedtest",
                   "text": message
               }]
               )


# TeamCity vars
project = "project name"  # Unusable
tcToken = "put your token"  # TeamCity token
tcProjectBuild = "put your build name"  # TeamCity build name
tcHost = "http://teamcity.host"  # TeamCity host

tcHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + tcToken}
results_json = 'results.json'
urls = "pagespeed_urls.txt"

# Get build numbers from TC
tcTwoLastSuccess = f'{tcHost}/app/rest/buildTypes/id:{tcProjectBuild}/builds?locator=status:SUCCESS,count:2'  # Get 2 last success builds from TC API
r = requests.get(tcTwoLastSuccess, headers=tcHeaders, timeout=10)
tcTwoLastFinal = r.json()

preLastBuildNum = str(tcTwoLastFinal['build'][1]['number'])
preLastBuildUrl = str(tcTwoLastFinal['build'][1]['webUrl'])

lastBuildNum = str(tcTwoLastFinal['build'][0]['number'])
lastBuildUrl = str(tcTwoLastFinal['build'][0]['webUrl'])

with open(results_json) as json_file:
    json_data = json.loads(json_file.read())
    json_file.close()

with open(urls) as pagespeedurls:
    content = pagespeedurls.readlines()
    content = [line.rstrip('\n') for line in content]
    for line in content:
        try:
            FCP_last = json_data[lastBuildNum][line]["FCP"]
            FI_last = json_data[lastBuildNum][line]["FI"]
            FCP_preLast = json_data[preLastBuildNum][line]["FCP"]
            FI_preLast = json_data[preLastBuildNum][line]["FI"]
        except Exception as keyErr:
            print("Key", keyErr, "not found")
            print("Check build number on CI/CD or run more speedtests for comparing!")
            exit(1)

        if float(FCP_last) > float(FCP_preLast):
            message = f'*URL*: {line}\n*Latest build:* _{lastBuildNum}_\n*FI:* _{FCP_last}_\n\n*Previous build:* _{preLastBuildNum}_\n*FI*: _{FCP_preLast}_\n*Build url:* {lastBuildUrl}'
            sendMessage(message)
        if float(FI_last) > float(FI_preLast):
            message = f'*URL*: {line}\n*Latest build:* _{lastBuildNum}_\n*FI:* _{FI_last}_\n\n*Previous build:* _{preLastBuildNum}_\n*FI*: _{FI_preLast}_\n*Build url:* {lastBuildUrl}'
            sendMessage(message)
