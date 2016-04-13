import requests,json
from pprint  import pprint
from celery import Celery,task

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'#'RC4-SHA'
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

celery = Celery('create_json', broker='amqp://guest@localhost//')
@celery.task()
def create_json():
	# Saving the json data to respective files for OVM
	Vm1 = session.get(baseUri1+'/Vm')
	Vm2 = session.get(baseUri2+'/Vm')
	Vm = Vm1.json()+Vm2.json()
	with open('webapp/JSON/vm.json', 'w') as outfile:
		json.dump(Vm, outfile)

	Server1 = session.get(baseUri1+'/Server')
	Server2 = session.get(baseUri2+'/Server')
	Server = Server1.json()+Server2.json()
	with open('webapp/JSON/server.json', 'w') as outfile:
		json.dump(Server, outfile)

	Repo1 = session.get(baseUri1+'/Repository')
	Repo2 = session.get(baseUri2+'/Repository')
	Repo = Repo1.json()+Repo2.json()
	with open('webapp/JSON/repo.json', 'w') as outfile:
		json.dump(Repo, outfile)

	StorageElem1 = session.get(baseUri1+'/StorageElement')
	StorageElem2 = session.get(baseUri2+'/StorageElement')
	StorageElem = StorageElem1.json()+StorageElem2.json()
	with open('webapp/JSON/storagelem.json', 'w') as outfile:
		json.dump(StorageElem, outfile)

	VirtualDisk1 = session.get(baseUri1+'/VirtualDisk')
	VirtualDisk2 = session.get(baseUri2+'/VirtualDisk')
	VirtualDisk = VirtualDisk1.json()+VirtualDisk2.json()
	with open('webapp/JSON/virtualdisk.json', 'w') as outfile:
		json.dump(VirtualDisk, outfile)

	VmDiskMapping1 = session.get(baseUri1+'/VmDiskMapping')
	VmDiskMapping2 = session.get(baseUri2+'/VmDiskMapping')
	VmDiskMapping = VmDiskMapping1.json() + VmDiskMapping2.json()
	with open('webapp/JSON/vmdiskmapping.json', 'w') as outfile:
		json.dump(VmDiskMapping, outfile)
	
	
	# Saving the JSON data for INFINIBOX
	host_list=inf_session.get(host_baseUri+"?page_size="+str(PAGE_SIZE))
	host_list_json=host_list.json()

	host_list2=inf_session.get(host_baseUri2+"?page_size="+str(PAGE_SIZE))
	host_list_json2=host_list2.json()

	host_list3=inf_session.get(host_baseUri3+"?page_size="+str(PAGE_SIZE))
	host_list_json3=host_list3.json()

	host_data = host_list_json['result']+host_list_json2['result']+host_list_json3['result']

	volume_list = inf_session.get(vol_baseUri+"?page_size="+str(PAGE_SIZE))
	volume_list_json = volume_list.json()

	volume_list2 = inf_session.get(vol_baseUri2+"?page_size="+str(PAGE_SIZE))
	volume_list_json2 = volume_list2.json()
	
	volume_list3 = inf_session.get(vol_baseUri3+"?page_size="+str(PAGE_SIZE))
	volume_list_json3 = volume_list3.json()

	volume_data = volume_list_json['result'] + volume_list_json2['result']+volume_list_json3['result']
	with open('webapp/JSON/infini_vol.json', 'w') as outfile:
		json.dump(volume_data, outfile)

	with open('webapp/JSON/infini_host.json', 'w') as outfile:
		json.dump(host_data, outfile)

	
	"""volume_list = inf_session.get(vol_baseUri+"?page_size="+str(PAGE_SIZE))
	volume_list_json = volume_list.json()
	
	host_list=inf_session.get(host_baseUri+"?page_size="+str(PAGE_SIZE))
	host_list_json=host_list.json()
	
	with open('webapp/JSON/infini_vol.json', 'w') as outfile:
	    json.dump(volume_list_json, outfile)
	
	with open('webapp/JSON/infini_host.json', 'w') as outfile:
	    json.dump(host_list_json, outfile)"""
	


	#Saving the 3par JSOn data from 2 IPs (10.62.100.6, 10.66.100.6, 10.62.100.117)
	from hp3parclient import client, exceptions
	username='juice'
	password='tcs_juice'
	vluns = []
	
	host='10.66.100.6'
	cl = client.HP3ParClient("https://%s:8080/api/v1" % host)
	cl.login(username, password)
	volumes1 = cl.getVolumes()['members']
	hosts1 = cl.getHosts()['members']
	vluns1 = cl.getVLUNs()['members']

	host2='10.62.100.6'
	cl2 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
	cl2.login(username, password)
	volumes2 = cl2.getVolumes()['members']
	hosts2 = cl2.getHosts()['members']
	vluns2 = cl2.getVLUNs()['members']

	host3 = '10.62.100.117'
	cl3 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
	cl3.login(username, password)
	volumes3 = cl3.getVolumes()['members']
	hosts3 = cl3.getHosts()['members']
	vluns3 = cl3.getVLUNs()['members']

	volume_data = volumes1+volumes2+volumes3
	host_data = hosts1+hosts2+hosts3
	vluns = vluns1+vluns2+vluns3

	"""for host in hosts1:
		try:
			vluns += cl.getHostVLUNs(host['name'])
		except:
			pass
	for host in hosts2:
		try:
			vluns += cl2.getHostVLUNs(host['name'])
		except:
			pass
	for host in hosts3:
		try:
			vluns += cl3.getHostVLUNs(host['name'])
		except:
			pass"""

	with open('webapp/JSON/3par_vol.json', 'w') as outfile:
		json.dump(volume_data, outfile)
	with open('webapp/JSON/3par_host.json', 'w') as outfile:
		json.dump(host_data, outfile)
	with open('webapp/JSON/3par_vlun.json', 'w') as outfile:
	    json.dump(vluns, outfile)
	cl.logout()
	cl2.logout()
	cl3.logout()





	#Saving VMware data for 10.62.100.15, 10.66.100.15
	from pyVim.connect import SmartConnect, Disconnect
	from pyVmomi import vim, vmodl
	import argparse
	import atexit
	import getpass
	import ssl

	"""
	Simple command-line program for listing the virtual machines on a system.
	"""
	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	context.verify_mode = ssl.CERT_NONE
	si = SmartConnect(host='10.62.100.15',#'chdcvcent01.tricoresolutions.com'
                     user='svc-juice',
                     pwd='bnDhPNavNs@^64Y-',
                     port=int(443),
                     sslContext=context)
	content = si.RetrieveContent()
	result = []
	objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
	for vm in objview.view:
		repo_dict = {}
		repo_dict['vmhost'] = vm.runtime.host.name
		repo_dict['vmname'] = vm.config.name
		repo_dict['vmware_disklist'] = []
		hardware = vm.config.hardware
		for each_vm_hardware in hardware.device:
			if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
				tmp_dict = {}
				reponame = each_vm_hardware.backing.fileName.split(']')[0]
				tmp_dict['reponame'] = reponame[1:]
				disk = each_vm_hardware.backing.fileName.split('/')[1]
				tmp_dict['disk'] = disk
				tmp_dict['capacity'] = each_vm_hardware.capacityInKB/1024/1024
				repo_dict['vmware_disklist'].append(tmp_dict)
		result.append(repo_dict)
	si = SmartConnect(host='10.66.100.15',
                     user='svc-juice',
                     pwd='bnDhPNavNs@^64Y-',
                     port=int(443),
                     sslContext=context)
	content = si.RetrieveContent()
	objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
	for vm in objview.view:
		repo_dict = {}
		repo_dict['vmhost'] = vm.runtime.host.name
		repo_dict['vmname'] = vm.config.name
		repo_dict['vmware_disklist'] = []
		hardware = vm.config.hardware
		for each_vm_hardware in hardware.device:
			if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
				tmp_dict = {}
				reponame = each_vm_hardware.backing.fileName.split(']')[0]
				tmp_dict['reponame'] = reponame[1:]
				disk = each_vm_hardware.backing.fileName.split('/')[1]
				tmp_dict['disk'] = disk
				tmp_dict['capacity'] = each_vm_hardware.capacityInKB/1024/1024
				repo_dict['vmware_disklist'].append(tmp_dict)
		result.append(repo_dict)
	with open('webapp/JSON/vmware.json', 'w') as outfile:
		json.dump(result, outfile)
