# ------All the utility functions related to OVM and User authentication are avilable here 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys,certifi
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

def bytesto(bytes, to, bsize=1024):
        unit = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
        result = float(bytes)
        for i in range(unit[to]):
                result = result / bsize
        return(result)

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
def applyfilter(hostidlist=[],cust_grp_acronym='',server = [],server_acronym='',source = 1):
	hostlist = []
	if source ==1:
		for vm in vmdata:
			if len(hostidlist) > 0  and vm['id']['name'] in hostidlist and vm not in hostlist:
				hostlist.append(vm)	
			elif cust_grp_acronym != '' and  cust_grp_acronym.lower() in vm['id']['name'].lower() and vm not in hostlist:
				hostlist.append(vm)
			if len(server) != 0 :
				if vm['id']['name'] in server and vm not in hostlist:
				        hostlist.append(vm)
	if source ==2:
		for host in infini_host_data:#['result']:
			if len(hostidlist) > 0  and str(host['name']) in hostidlist and host not in hostlist:
                                hostlist.append(host)

			elif cust_grp_acronym != '' and cust_grp_acronym.lower() in host['name'].lower() and host not in hostlist:
				hostlist.append(host)
			if  len(server) != 0 :
				if str(host['name']) in server:
					 hostlist.append(host)
			elif server_acronym != '' and server_acronym.lower() in host['name'].lower() and host not in hostlist:
				hostlist.append(host)
			
	if source ==3:
		tmp_list = []
		for par3_host in par3Host_data :#['members']:
			if 'name' in par3_host  and 'id' in par3_host:
				if len(hostidlist) > 0 and str(par3_host['name']) in hostidlist and par3_host not in hostlist:
					hostlist.append(par3_host)
				elif cust_grp_acronym != '' and cust_grp_acronym.lower() in par3_host['name'].lower() and par3_host not in hostlist:
					hostlist.append(par3_host)
				if len(server) != 0:
					if str(par3_host['name']) in server:
						hostlist.append(par3_host)
				elif server_acronym != '' and server_acronym.lower() in par3_host['name'].lower() and par3_host not in hostlist:
					hostlist.append(par3_host)
	return  hostlist

#--------Module to get server/host names from all hosts across OVM/infini/3par/VMWare ------#
def get_servernames(cust_grp = "",hostidlist = []):
	ovm_vmlist = []
	infini_serverlist = []
	par3_serverlist = []
	for vm in vmdata:
		if cust_grp != '' and  cust_grp.lower() in vm['id']['name'].lower():
			ovm_vmlist.append(vm['id']['name'])
		elif len(hostidlist) > 0 and vm['id']['value'] in hostidlist:
			ovm_vmlist.append(vm['id']['name'])	
	for server in infini_host_data : #['result']:		
		if cust_grp != '' and cust_grp.lower() in server['name'].lower():
			infini_serverlist.append(server['name'])
		elif len(hostidlist) > 0 and str(server['id']) in hostidlist:
			infini_serverlist.append(server['name'])	
	for host in par3Host_data:#['members']:
		if 'id' in host and 'name' in host:
			if cust_grp != '' and cust_grp.lower() in host['name'].lower():
				par3_serverlist.append(host['name'])
			elif len(hostidlist) > 0 and str(host['id']) in hostidlist:
				par3_serverlist.append(host['name'])	
	return ( ovm_vmlist,infini_serverlist,par3_serverlist)
	
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

def get_ovm_serverlist():
	ovm_serverlist = []
	for vm in vmdata:
		ovm_serverlist.append(vm['name'])
	return ovm_serverlist

def get_ovm(vlist):
	total_usage= 0
	res_dict  = {}
	try:
		if len(vlist) == 0:
			vlist = [vm  for  vm in vmdata]

		for v in vlist:
			serverId = v['serverId']
			if not serverId:
				continue;
			servername = serverId.get('name') if serverId else 'None'
			if serverId['name'] not in  res_dict:
				res_dict[servername] = {}
				res_dict[servername] ['physicalist']  = []
				res_dict[servername]['virtualist'] = []
				res_dict[servername]['total_size'] = 0

			id = v['id']['value']
			res_dict[servername]['vmname'] = v['id']['name']

			for disk in vmdiskmapping_data:
				if disk['vmId']['value'] == id and disk['storageElementId']!= None:
						diskname =  disk.get('storageElementId').get('name') if disk.get('storageElementId').get('name') else 'None'
						physical_dict = {}
						physical_dict['name'] = diskname
						physicaldisk_id = disk.get('storageElementId').get('value')
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
							res_dict[servername]['total_size'] += int(physical_disk_size)
							physical_dict['total'] += int(physical_disk_size)
						physical_dict['repo_name'] = ""
						res_dict[servername]['physicalist'].append(physical_dict)
				elif  disk['vmId']['value'] == id and disk.get('virtualDiskId') != None:
						diskname = disk.get('virtualDiskId').get('name') if disk.get('virtualDiskId').get('name') else 'None'
						virtual_dict = {}
						virtual_dict['name'] = diskname
						virtualdisk_id = disk.get('virtualDiskId').get('value')
						virtual_dict['id'] = virtualdisk_id
						virtual_dict['total'] = 0
						#for virtual disk size and repo name
						for virtualdisk in virtualdiskdata:
							if virtualdisk['id']['value'] == str(virtualdisk_id):
								virtualdiskObj = virtualdisk
						virtual_disk_size = bytesto(virtualdiskObj['onDiskSize'],'g')
						virtual_dict['size'] = virtual_disk_size
						if  virtualdiskObj.get('repositoryId'):
							virtual_dict['repo_name'] = virtualdiskObj['repositoryId']['name']
						if not any(substr in diskname.lower() for substr in exclude_list):
							#for total vm size
							total_usage += int(virtual_disk_size) 
							res_dict[servername]['total_size'] += int(virtual_disk_size)
							virtual_dict['total'] += int(virtual_disk_size)
						res_dict[servername]['virtualist'].append(virtual_dict)
			res_dict[servername]['vm_name']= v['id']['name']
			res_dict[servername]['disk_list']  = res_dict[servername]['virtualist']+res_dict[servername]['physicalist']
	except Exception as e:
		reslist = "Error in OVM calculation - "+str( e)
	return (res_dict,total_usage)


