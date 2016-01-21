import requests,json
from pprint  import pprint
from celery import Celery,task

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'RC4-SHA'
session=requests.Session()
session.verify= False #disables SSL certificate verification
session.auth=('juice','tcs_juice')
session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri='https://smdcovmm01.tricorems.com:7002/ovm/core/wsapi/rest'

inf_session = requests.Session()
inf_session.auth=('juice','Svc-ju1c3') # supply auth info
inf_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
inf_session.verify=False #disables SSL certificate verification
PAGE_SIZE =1000
vol_baseUri = 'https://10.62.100.156//api/rest/volumes'
host_baseUri='https://10.62.100.156//api/rest/hosts'

"""
celery = Celery('create_json', broker='amqp://guest@localhost//')
@task()
def create_json():
	# Saving the json data to respective files for OVM
	Vm = session.get(baseUri+'/Vm')
	with open('webapp/JSON/vm.json', 'w') as outfile:
	    json.dump(Vm.json(), outfile)
	
	Server = session.get(baseUri+'/Server')
	with open('webapp/JSON/server.json', 'w') as outfile:
	    json.dump(Server.json(), outfile)
	
	Repo = session.get(baseUri+'/Repository')
	with open('webapp/JSON/repo.json', 'w') as outfile:
	    json.dump(Repo.json(), outfile)

	StorageElem = session.get(baseUri+'/StorageElement')
	with open('webapp/JSON/storagelem.json', 'w') as outfile:
		json.dump(StorageElem.json(), outfile)

	VirtualDisk = session.get(baseUri+'/VirtualDisk')
	with open('webapp/JSON/virtualdisk.json', 'w') as outfile:
		json.dump(VirtualDisk.json(), outfile)

	VmDiskMapping = session.get(baseUri+'/VmDiskMapping')
	with open('webapp/JSON/vmdiskmapping.json', 'w') as outfile:
		json.dump(VmDiskMapping.json(), outfile)


	
	
	
	# Saving the JSON data for INFINIBOX
	volume_list = inf_session.get(vol_baseUri+"?page_size="+str(PAGE_SIZE))
	volume_list_json = volume_list.json()
	
	host_list=inf_session.get(host_baseUri+"?page_size="+str(PAGE_SIZE))
	host_list_json=host_list.json()
	
	with open('webapp/JSON/infini_vol.json', 'w') as outfile:
	    json.dump(volume_list_json, outfile)
	
	with open('webapp/JSON/infini_host.json', 'w') as outfile:
	    json.dump(host_list_json, outfile)
	

"""
with open('JSON/vmdiskmapping.json') as data_file:
	data = json.load(data_file)
for d in data:
	pprint (d)

