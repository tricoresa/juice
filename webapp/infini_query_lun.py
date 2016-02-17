#!/usr/bin/python
#****************************************************************************
#
# Script to fetch infinibox volume details provided the hostname and Lunid
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
parser.add_argument("--lunid", help="Lun Id")
parser.add_argument("--hostname", help="hostname")
parser.add_argument("--infinibox", help="infinibox IP")
args = parser.parse_args()
reslist = []
vol_id= 0
hostname=args.hostname or ''
lun_id = int(args.lunid or 0) 
infinibox = args.infinibox or ''

baseUri = 'https://'+str(infinibox)+'//api/rest'
volume_list = inf_session.get(baseUri+"/volumes?page_size="+str(PAGE_SIZE))
infini_volume_data = volume_list.json()
host_list = inf_session.get(baseUri+"/hosts?page_size="+str(PAGE_SIZE)) 
infini_host_data = host_list.json()
for host  in infini_host_data['result']:
	if hostname == str(host['name']):
		for lun in host['luns']:
			if lun_id != 0 and lun_id == lun['lun']:
				vol_id = lun['volume_id']
for vol in infini_volume_data['result']:
	if vol_id != 0 :
		if vol['id'] == vol_id:
			result = {"volumeid":vol['id'],"volume_name":vol['name'],"wwid":vol['serial']}
			reslist.append(result)
	#else:
	#	result = {"volumeid":vol['id'],"volume_name":vol['name'],"wwid":vol['serial']}
	#	reslist.append(result)

if len(reslist) > 0:
	print (reslist)
else:
	print ("No volume found for the hostname and lunid combination")




# Django classs based structure for the same
"""
class InfiniDetails2(View):
	def get(self,request):
		reslist = []
		hostname = self.request.GET.get('hostname') or ''
		lun_id = int(self.request.GET.get('lunid') or 0)
		vol_id= 0
		for host  in infini_host_data['result']:
			for lun in host['luns']:
				if (lun_id != 0 and lun_id == lun['lun'] and  hostname != '' and hostname == host['name']):
					vol_id = lun['volume_id']
		for vol in infini_volume_data['result']:
			if vol_id != 0 :
				if vol['id'] == vol_id:
					result = {"volumeid":vol['id'],"volume_name":vol['name'],"wwid":vol['serial']}
					reslist.append(result)
			else:
				result = {"volumeid":vol['id'],"volume_name":vol['name'],"wwid":vol['serial']}
				reslist.append(result)
				
		return HttpResponse(json.dumps(reslist))

class InfiniDetails(View):
	def get(self,request):
		wwid = self.request.GET.get('wwid') or ''
		reslist = []
		for vol in infini_volume_data['result']:
			if wwid != '':
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
		return HttpResponse (json.dumps(reslist))
"""
