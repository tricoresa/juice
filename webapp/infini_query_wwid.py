#!/usr/bin/python
#****************************************************************************
#
# Script to fetch infinibox volume details provided the wwid/volume serial number
#
#****************************************************************************
import json,requests
import argparse, subprocess

inf_session = requests.Session()
inf_session.auth=('juice','Svc-ju1c3') # supply auth info
inf_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
inf_session.verify=False #disables SSL certificate verification
PAGE_SIZE =1000

parser = argparse.ArgumentParser()
parser.add_argument("--wwid", help="wwid")
parser.add_argument("--infinibox", help="infinibox IP")
args = parser.parse_args()
wwid = args.wwid or ''
infinibox   = args.infinibox or ''
reslist = []
baseUri = 'https://'+str(infinibox)+'//api/rest'
volume_list = inf_session.get(baseUri+"/volumes?page_size="+str(PAGE_SIZE))
infini_volume_data = volume_list.json()
for vol in infini_volume_data['result']:
	if wwid != '' :
		if vol['serial'] == wwid:
			result = {}
			result["volumeid"]=vol['id']
			result["volume_name"]=vol['name']
			result["wwid"]=vol['serial']
			reslist.append(result)
	else:
		result = {}
		result["volumeid"]=vol['id']
		result["volume_name"]=vol['name']
		result["wwid"]=vol['serial']
		reslist.append(result)
print (reslist)
