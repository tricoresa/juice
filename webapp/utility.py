# ------All the utility functions related to OVM and User authentication are avilable here 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys,certifi,math
import requests,json
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'#'RC4-SHA'

Grp = {
'Superuser':0,
'Admin':1,
'Operator':2,
'Readonly':3
}
USER_GRP = {
'Admin' : 'auth.delete_user',
'Operator' :'',
'ReadOnly':''
}

#Read JSON files

with open('webapp/JSON/vm.json') as data_file:
        vmdata = json.load(data_file)
with open('webapp/JSON/server.json') as data_file:
        serverdata = json.load(data_file)
with open('webapp/JSON/repo.json') as data_file:
        repodata = json.load(data_file)
with open('webapp/JSON/storagelem.json') as data_file:
        storagelemdata = json.load(data_file)
with open('webapp/JSON/virtualdisk.json') as data_file:
        virtualdiskdata = json.load(data_file)
with open('webapp/JSON/infini_host.json') as data_file:
        infini_host_data = json.load(data_file)
with open('webapp/JSON/infini_vol.json') as data_file:
        infini_volume_data = json.load(data_file)
with open('webapp/JSON/vmdiskmapping.json') as data_file:
	vmdiskmapping_data = json.load(data_file)
with open('webapp/JSON/3par_host.json') as data_file:
        par3Host_data = json.load(data_file)
with open('webapp/JSON/3par_vol.json') as data_file:
        par3Volume_data = json.load(data_file)
with open('webapp/JSON/3par_vlun.json') as data_file:
        par3Vlun_data = json.load(data_file)
with open('webapp/JSON/vmware.json') as data_file:
        vmware_data = json.load(data_file)

def bytesto(bytes, to, bsize=1024):
        unit = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
        result = float(bytes)
        for i in range(unit[to]):
                result = result / bsize
        return (math.ceil(result))

session=requests.Session()
session.verify= False #disables SSL certificate verification
session.auth=('juice','tcs_juice')

session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

baseUri='https://smdcovmm01.tricorems.com:7002/ovm/core/wsapi/rest'
exclude_list = ['_root','system','swap']
def  login_required(user):
	if  not user.is_authenticated()  or  user.is_anonymous():
		return True
	else:
		return False
def get_user_grp(user):
	perm = user.get_group_permissions()
	if user.is_superuser:
		user_grp = Grp['Superuser']
	elif USER_GRP['Admin'] in  perm:
		user_grp = Grp['Admin']
	elif len(perm)> 0:
		user_grp = Grp['Operator']
	else:
		user_grp = Grp['Readonly']
	return user_grp

#---- Pagination module (generic) ----#
def pagination(obj,limit,page=1):
        paginator = Paginator(obj,limit)
        try:
                pagination_res = paginator.page(page)
        except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                pagination_res = paginator.page(1)
        except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                pagination_res = paginator.page(paginator.num_pages)
        return pagination_res

#------Module to apply the user defined filter of customer group or server/host name to get the specific Host(s) details -------#
def applyfilter(cust_acronym_list=[],server=[],server_acronym=''):
	hostlist = []
	for vm in vmdata:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if vm.get('id').get('name'):
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if cust_grp_acronym.lower() in vm['id']['name'].lower() and vm not in hostlist:
						hostlist.append(vm)
				else:
					if '!' in cust_grp_acronym and  cust_grp_acronym[1:]  in vm['id']['name'].lower() and vm in hostlist:
						hostlist.remove(vm)
		if len(server) != 0 :
			if vm.get('id').get('name') and vm['id']['name'] in server and vm not in hostlist:
				hostlist.append(vm)
		if vm.get('id').get('name') and server_acronym != '' and server_acronym.lower() in vm['id']['name'].lower() and vm not in hostlist:
			hostlist.append(vm)



	for host in infini_host_data:#['result']:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'name' in host:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in host['name'].lower() and host not in hostlist:
						hostlist.append(host)
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in host['name'].lower() and host in hostlist:
						hostlist.remove(host)
		if  len(server) != 0 :
			if str(host['name']) in server and host not in hostlist:
				hostlist.append(host)
		if server_acronym != '' and server_acronym.lower() in host['name'].lower() and host not in hostlist:
			hostlist.append(host)


	for par3_host in par3Host_data :#['members']:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'name' in par3_host:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in par3_host['name'].lower() and par3_host not in hostlist:
						hostlist.append(par3_host)
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in par3_host['name'].lower() and par3_host in hostlist:
                                                hostlist.remove(par3_host)
		if len(server) != 0:
			if 'name' in par3_host and str(par3_host['name']) in server and par3_host not in hostlist:
				hostlist.append(par3_host)
		if 'name' in par3_host and server_acronym != '' and server_acronym.lower() in par3_host['name'].lower() and par3_host not in hostlist:
			hostlist.append(par3_host)


	for vmware in vmware_data:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'vmname' in vmware:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in vmware['vmname'].lower() and vmware not in hostlist:
						hostlist.append(vmware)
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in vmware['vmname'].lower() and vmware in hostlist:
                                                hostlist.remove(vmware)
		if len(server) != 0 :
			if vmware['vmname'] in server and vmware not in hostlist:
				hostlist.append(vmware)
		if server_acronym != '' and server_acronym.lower() in vmware['vmname'].lower() and vmware not in hostlist:
			hostlist.append(vmware)
	return  hostlist

#--------Module to get server/host names from all hosts across OVM/infini/3par/VMWare ------#
def get_servernames(cust_acronym_list = []):
	hostlist = []
	for vm in vmdata:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if vm.get('id').get('name'):
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if cust_grp_acronym.lower() in vm['id']['name'].lower() and vm['id']['name'] not in hostlist:
						hostlist.append(vm['id']['name'])
				else:
					if '!' in cust_grp_acronym and  cust_grp_acronym[1:]  in vm['id']['name'].lower() and vm['id']['name'] in hostlist:
						hostlist.remove(vm['id']['name'])
	for host in infini_host_data:#['result']:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'name' in host:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in host['name'].lower() and host['name'] not in hostlist:
						hostlist.append(host['name'])
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in host['name'].lower() and host['name'] in hostlist:
						hostlist.remove(host['name'])	
	for par3_host in par3Host_data :#['members']:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'name' in par3_host:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in par3_host['name'].lower() and par3_host['name'] not in hostlist:
						hostlist.append(par3_host['name'])
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in par3_host['name'].lower() and par3_host['name'] in hostlist:
						hostlist.remove(par3_host['name'])
	for vmware in vmware_data:
		for cust_grp_acronym in cust_acronym_list:
			cust_grp_acronym = cust_grp_acronym.strip()
			if 'vmname' in vmware:
				if cust_grp_acronym != '' and '!' not in cust_grp_acronym:
					if  cust_grp_acronym.lower() in vmware['vmname'].lower() and vmware['vmname'] not in hostlist:
						hostlist.append(vmware['vmname'])
				else:
					if '!' in cust_grp_acronym and cust_grp_acronym[1:] in vmware['vmname'].lower() and vmware['vmname'] in hostlist:
						hostlist.remove(vmware['vmname'])
	return hostlist
# --- Details of OVM repositories ----#
def get_repo_detail(repoid):
	repoFileIds = session.get(baseUri+'/Repository/'+str(repoid)+'/FileSystem')
	res_dict = {}
	res_dict['reponame'] = repoFileIds.json()['repositoryIds'][0]['name']
	size = repoFileIds.json()['size']
	res_dict['size'] = bytesto(size,'g')
	freesize = repoFileIds.json()['freeSize']
	res_dict['freesize'] = bytesto(freesize,'g')
	usedsize  = size-freesize
	res_dict['usedsize'] = bytesto(usedsize,'g')
	return res_dict

# ---------List of all the unique VMs in OVM -------------- #
def get_ovm_serverlist():
	ovm_serverlist = []
	for vm in vmdata:
		if 'name' in vm and vm['name']!= '':
			ovm_serverlist.append(vm['name'])
	return ovm_serverlist

# ------------- List of unmapped VM in OVM ----------- #
def get_unmapped_ovm():
	reslist = []
	error = ''
	try:
		for virtual in virtualdiskdata:
			res_dict = {}
			if virtual['vmDiskMappingIds'] == []:
				res_dict['name'] = virtual['name']
				res_dict['id'] = virtual['id']['value']
				res_dict['size']= bytesto(virtual['size'],'g')
				reslist.append(res_dict)
		for storage in storagelemdata:
			res_dict = {}
			if storage['vmDiskMappingIds'] == []:
				res_dict['name'] = storage['name']
				res_dict['id'] = storage['id']['value']
				res_dict['size']= bytesto(storage['size'],'g')
				reslist.append(res_dict)
	except  Exception as e:
		error = "Error in OVM calculation - "+str(e)

	return (reslist,error)

# -------------Get VM from OVM and its respective Virtual and physical disks/repo details on the basis of selected VMs ------ #
def get_ovm(vlist):
	total_usage= 0
	disk_list = []
	error = ''
	res_dict  = {}
	try:
		if len(vlist) == 0:
			vlist = [vm  for  vm in vmdata]
		for v in vlist:
			serverId = v.get('serverId')
			if not serverId:
				continue;
			servername = serverId.get('name') if serverId else 'None'
			vmname = v['id']['name']
			if vmname not in  res_dict:
				res_dict[vmname] = {}
				res_dict[vmname]['source'] = 'OVM'
				res_dict[vmname]['vm_name'] = vmname
				res_dict[vmname] ['physicalist']  = []
				res_dict[vmname]['virtualist'] = []
				res_dict[vmname]['disk_list'] = []
				res_dict[vmname]['total_size'] = 0
				res_dict[vmname]['servername'] = servername
			id = v['id']['value']
			for disk in vmdiskmapping_data:
				if disk['vmId']['value'] == id and disk['storageElementId']!= None:
					diskname =  disk.get('storageElementId').get('name') if disk.get('storageElementId').get('name') else 'None'
					diskid = disk.get('storageElementId').get('value')
					if diskid not in disk_list:
						# remove duplicate physical_disks from the OVM report
						disk_list.append(diskid)
						physical_dict = {}
						physical_dict['name'] = diskname
						physical_dict['source'] = 'OVM'
						physicaldisk_id = diskid
						physical_dict['id'] = physicaldisk_id

						#for physical disk size
						for storage in storagelemdata:
							if storage['id']['value'] == str(physicaldisk_id):
								storageObj = storage
						physical_disk_size = bytesto(storageObj['size'],'g')
						physical_dict['size'] = physical_disk_size
						physical_dict['total'] = 0
						if not any(substr in diskname.lower() for substr in exclude_list):
							#for total vm size
							total_usage += int(physical_disk_size) 
							res_dict[vmname]['total_size'] += int(physical_disk_size)
							physical_dict['total'] += int(physical_disk_size)
						physical_dict['repo_name'] = ""
						res_dict[vmname]['physicalist'].append(physical_dict)
				elif  disk['vmId']['value'] == id and disk.get('virtualDiskId') != None:
					diskname = disk.get('virtualDiskId').get('name') if disk.get('virtualDiskId').get('name') else 'None'
					diskid = disk.get('virtualDiskId').get('value')
					if diskid not in disk_list:
						#------------- remove duplicate virtual_lists from OVM report
						disk_list.append(diskid)
						virtual_dict = {}
						virtual_dict['name'] = diskname
						virtual_dict['source'] = 'OVM'
						virtualdisk_id = diskid
						virtual_dict['id'] = virtualdisk_id
						virtual_dict['total'] = 0
						#------------for virtual disk size and repo name
						for virtualdisk in virtualdiskdata:
							if virtualdisk['id']['value'] == str(virtualdisk_id):
								virtualdiskObj = virtualdisk
						virtual_disk_size = bytesto(virtualdiskObj['onDiskSize'],'g')
						virtual_dict['size'] = virtual_disk_size
						if  virtualdiskObj.get('repositoryId'):
							virtual_dict['repo_name'] = virtualdiskObj['repositoryId']['name']
						if not any(substr in diskname.lower() for substr in exclude_list):
							#----------------for total vm size
							total_usage += int(virtual_disk_size) 
							res_dict[vmname]['total_size'] += int(virtual_disk_size)
							virtual_dict['total'] += int(virtual_disk_size)
						res_dict[vmname]['virtualist'].append(virtual_dict)
			res_dict[vmname]['disk_list']  = res_dict[vmname]['virtualist']+res_dict[vmname]['physicalist']
			#if vmname in res_dict and len(res_dict[vmname]['disk_list']) == 0:
			#	res_dict.pop(vmname,None)
	except Exception as e:
		error  = "Error in OVM calculation - "+str( e)
	return (res_dict,total_usage,error)


