import requests,json,operator
from pprint  import pprint
import os.path
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'RC4-SHA'
session=requests.Session()
session.verify= False #disables SSL certificate verification
session.auth=('juice','tcs_juice')
session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri1='https://10.62.100.88:7002/ovm/core/wsapi/rest'
baseUri2='https://10.66.100.67:7002/ovm/core/wsapi/rest'

inf_session = requests.Session()
inf_session.auth=('juice','Svc-ju1c3') # supply auth info
inf_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
inf_session.verify=False #disables SSL certificate verification
PAGE_SIZE =1000
vol_baseUri = 'https://10.62.100.156//api/rest/volumes'
host_baseUri='https://10.62.100.156//api/rest/hosts'
vol_baseUri2 = 'https://10.62.100.174//api/rest/volumes'
host_baseUri2='https://10.62.100.174//api/rest/hosts'
vol_baseUri3 = 'https://10.66.100.85//api/rest/volumes'
host_baseUri3='https://10.66.100.85//api/rest/hosts'



# Saving the json data to respective files for OVM
Vm1 = session.get(baseUri1+'/Vm')
Vm2 = session.get(baseUri2+'/Vm')
Vm = Vm1.json()+Vm2.json()
with open('JSON/vm.json', 'w') as outfile:
    json.dump(Vm, outfile)

Server1 = session.get(baseUri1+'/Server')
Server2 = session.get(baseUri2+'/Server')
Server = Server1.json()+Server2.json()
with open('JSON/server.json', 'w') as outfile:
    json.dump(Server, outfile)

Repo1 = session.get(baseUri1+'/Repository')
Repo2 = session.get(baseUri2+'/Repository')
Repo = Repo1.json()+Repo2.json()
with open('JSON/repo.json', 'w') as outfile:
    json.dump(Repo, outfile)

StorageElem1 = session.get(baseUri1+'/StorageElement')
StorageElem2 = session.get(baseUri2+'/StorageElement')
StorageElem = StorageElem1.json()+StorageElem2.json() 
with open('JSON/storagelem.json', 'w') as outfile:
        json.dump(StorageElem, outfile)

VirtualDisk1 = session.get(baseUri1+'/VirtualDisk')
VirtualDisk2 = session.get(baseUri2+'/VirtualDisk')
VirtualDisk = VirtualDisk1.json()+VirtualDisk2.json() 
with open('JSON/virtualdisk.json', 'w') as outfile:
        json.dump(VirtualDisk, outfile)

VmDiskMapping1 = session.get(baseUri1+'/VmDiskMapping')
VmDiskMapping2 = session.get(baseUri2+'/VmDiskMapping')
VmDiskMapping = VmDiskMapping1.json() + VmDiskMapping2.json()
with open('JSON/vmdiskmapping.json', 'w') as outfile:
	json.dump(VmDiskMapping, outfile)
"""
# Saving the JSON data for INFINIBOX

host_list=inf_session.get(host_baseUri+"?page_size="+str(PAGE_SIZE))
host_list_json=host_list.json()

host_list2=inf_session.get(host_baseUri2+"?page_size="+str(PAGE_SIZE))
host_list_json2=host_list2.json()

host_list3=inf_session.get(host_baseUri3+"?page_size="+str(PAGE_SIZE))
host_list_json3=host_list3.json()
host_data = host_list_json['result']+host_list_json2['result'] +host_list_json3['result']

volume_list = inf_session.get(vol_baseUri+"?page_size="+str(PAGE_SIZE))
volume_list_json = volume_list.json()

volume_list2 = inf_session.get(vol_baseUri2+"?page_size="+str(PAGE_SIZE))
volume_list_json2 = volume_list2.json()

volume_list3 = inf_session.get(vol_baseUri3+"?page_size="+str(PAGE_SIZE))
volume_list_json3 = volume_list3.json()

volume_data = volume_list_json['result'] + volume_list_json2['result']+volume_list_json3['result']
with open('JSON/infini_vol.json', 'w') as outfile:
	json.dump(volume_data, outfile)

with open('JSON/infini_host.json', 'w') as outfile:
	json.dump(host_data, outfile)
"""

