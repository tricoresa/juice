import requests,json,operator
from pprint  import pprint
import os.path
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'RC4-SHA'
session=requests.Session()
session.verify= False #disables SSL certificate verification
session.auth=('juice','tcs_juice')
session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
baseUri1='10.62.100.88'
baseUri2='10.66.100.67'

inf_session = requests.Session()
inf_session.auth=('juice','Svc-ju1c3') # supply auth info
inf_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
inf_session.verify=False #disables SSL certificate verification
PAGE_SIZE =1000
infini_baseUri1 = '10.62.100.156'
infini_baseUri2 = '10.62.100.174'
infini_baseUri3 = '10.66.100.85'

"""

# Saving the json data to respective files for OVM
Vm1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/Vm')
Vm2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/Vm')
Vm = Vm1.json()+Vm2.json()
with open('JSON/vm.json', 'w') as outfile:
    json.dump(Vm, outfile)

Server1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/Server')
Server2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/Server')
Server = Server1.json()+Server2.json()
with open('JSON/server.json', 'w') as outfile:
    json.dump(Server, outfile)

Repo1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/Repository')
Repo2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/Repository')
Repo = Repo1.json()+Repo2.json()
with open('JSON/repo.json', 'w') as outfile:
    json.dump(Repo, outfile)

StorageElem1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/StorageElement')
StorageElem2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/StorageElement')
StorageElem = StorageElem1.json()+StorageElem2.json() 
with open('JSON/storagelem.json', 'w') as outfile:
        json.dump(StorageElem, outfile)

VirtualDisk1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/VirtualDisk')
VirtualDisk2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/VirtualDisk')
VirtualDisk = VirtualDisk1.json()+VirtualDisk2.json() 
with open('JSON/virtualdisk.json', 'w') as outfile:
        json.dump(VirtualDisk, outfile)

VmDiskMapping1 = session.get('https://'+baseUri1+':7002/ovm/core/wsapi/rest/VmDiskMapping')
VmDiskMapping2 = session.get('https://'+baseUri2+':7002/ovm/core/wsapi/rest/VmDiskMapping')
VmDiskMapping = VmDiskMapping1.json() + VmDiskMapping2.json()
with open('JSON/vmdiskmapping.json', 'w') as outfile:
	json.dump(VmDiskMapping, outfile)
"""
# Saving the JSON data for INFINIBOX

host_list=inf_session.get('https://'+ infini_baseUri1 +'//api/rest/hosts?page_size='+str(PAGE_SIZE))
host_list_json=host_list.json()
for host in host_list_json['result']:
    host['ip'] = infini_baseUri1
host_list2=inf_session.get('https://'+ infini_baseUri2 +'//api/rest/hosts?page_size='+str(PAGE_SIZE))
host_list_json2=host_list2.json()
for host in host_list_json2['result']:
    host['ip'] = infini_baseUri2
host_list3=inf_session.get('https://'+ infini_baseUri3 +'//api/rest/hosts?page_size='+str(PAGE_SIZE))
host_list_json3=host_list3.json()
for host in host_list_json3['result']:
    host['ip'] = infini_baseUri3
host_data = host_list_json['result']+host_list_json2['result'] +host_list_json3['result']

volume_list = inf_session.get('https://'+ infini_baseUri1 +'//api/rest/volumes?page_size='+str(PAGE_SIZE))
volume_list_json = volume_list.json()
for vol in volume_list_json['result']:
    vol['ip'] = infini_baseUri1
volume_list2 = inf_session.get('https://'+ infini_baseUri2 +'//api/rest/volumes?page_size='+str(PAGE_SIZE))
volume_list_json2 = volume_list2.json()
for vol in volume_list_json2['result']:
    vol['ip'] = infini_baseUri2
volume_list3 = inf_session.get('https://'+ infini_baseUri3 +'//api/rest/volumes?page_size='+str(PAGE_SIZE))
volume_list_json3 = volume_list3.json()
for vol in volume_list_json3['result']:
    vol['ip'] = infini_baseUri3
volume_data = volume_list_json['result'] + volume_list_json2['result']+volume_list_json3['result']
with open('JSON/infini_vol.json', 'w') as outfile:
	json.dump(volume_data, outfile)

with open('JSON/infini_host.json', 'w') as outfile:
	json.dump(host_data, outfile)


