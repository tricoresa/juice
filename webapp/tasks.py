import requests,json
from pprint  import pprint
from celery import Celery,task

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'#'RC4-SHA'
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

vol_baseUri2 = 'https://10.62.100.174//api/rest/volumes'
host_baseUri2='https://10.62.100.174//api/rest/hosts'

vol_baseUri3 = 'https://10.66.100.85//api/rest/volumes'
host_baseUri3='https://10.66.100.85//api/rest/hosts'

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
	with open('JSON/infini_vol.json', 'w') as outfile:
		json.dump(volume_data, outfile)

	with open('JSON/infini_host.json', 'w') as outfile:
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

	host2='10.62.100.6'
	cl2 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
	cl2.login(username, password)
	volumes2 = cl2.getVolumes()['members']
	hosts2 = cl2.getHosts()['members']

	host3 = '10.62.100.117'
	cl3 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
	cl3.login(username, password)
	volumes3 = cl2.getVolumes()['members']
	hosts3 = cl2.getHosts()['members']

	volume_data = volumes1+volumes2+volumes3
	host_data = hosts1+hosts2+hosts3

	for host in hosts1:
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
			pass

	with open('webapp/JSON/3par_vol.json', 'w') as outfile:
		json.dump(volume_data, outfile)
	with open('webapp/JSON/3par_host.json', 'w') as outfile:
		json.dump(host_data, outfile)
	with open('webapp/JSON/3par_vlun.json', 'w') as outfile:
	    json.dump(vluns, outfile)
	cl.logout()
	cl2.logout()

	#Saving VMware data for 10.62.100.15
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
	objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
	esxi_hosts = objview.view
	objview.Destroy()
	for esxi_host in esxi_hosts:
		res_dict = {}
		res_dict['hostname'] = esxi_host.name
		res_dict['vmwareDisk'] = []

		storage_system = esxi_host.configManager.storageSystem
		host_file_sys_vol_mount_info = storage_system.fileSystemVolumeInfo.mountInfo
		for host_mount_info in host_file_sys_vol_mount_info:
			if host_mount_info.volume.type == "VMFS":
				datastore_dict = {}
				datastore_dict['reponame'] = host_mount_info.volume.name
				extents = host_mount_info.volume.extent
				for extent in extents:
					datastore_dict['reponame'] = host_mount_info.volume.name
					datastore_dict['disk']  = extent.diskName
					datastore_dict['capacity'] = host_mount_info.volume.capacity
				res_dict['vmwareDisk'].append(datastore_dict)
		result.append(res_dict)
	with open('webapp/JSON/vmware.json', 'w') as outfile:
		json.dump(result, outfile)
