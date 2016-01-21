# ------All the utility functions related to OVM and User authentication are avilable here 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys,certifi
import requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'RC4-SHA'

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


# --- given a VM id list, this module calculate the disk size for each VM ---#
def calculate_size(groupObj):
	reslist = []
	total_usage = 0
	try:
		for vm in groupObj:
			vmIds = session.get(baseUri+'/Vm/'+str(vm))
			v = vmIds.json().get('id')
			if v:
				res_dict = {}
				total_size = 0
				physicalist = []
				virtualist = []
				id = v['value']
				res_dict['vmname'] = v['name']
				serverId = vmIds.json().get('serverId')
				res_dict['servername'] = serverId['name'] if serverId else "none"
				diskMapId = session.get(baseUri+'/Vm/'+str(id)+'/VmDiskMapping')
				for disk in diskMapId.json():
					if disk.get('storageElementId') != None:
						diskname =  disk.get('storageElementId').get('name') if disk.get('storageElementId').get('name') else 'None'
						physical_dict = {}
						physical_dict['name'] = diskname
						physicaldisk_id = disk.get('storageElementId').get('value')
						physical_dict['id'] = physicaldisk_id
				
						#for physical disk size
						storageObj = session.get(baseUri+'/StorageElement/'+str(physicaldisk_id))
						physical_disk_size = bytesto(storageObj.json()['size'],'g')
						physical_dict['size'] = physical_disk_size
						physical_dict['total'] = 0
						if not any(substr in diskname.lower() for substr in exclude_list):
							#for total vm size
							total_size += int(physical_disk_size)
							physical_dict['total'] += int(physical_disk_size)
						physical_dict['repo_name'] = ""
						physicalist.append(physical_dict)
					elif disk.get('virtualDiskId') != None:
						diskname = disk.get('virtualDiskId').get('name') if disk.get('virtualDiskId').get('name') else 'None'
						virtual_dict = {}
						virtual_dict['name'] = diskname
						virtualdisk_id = disk.get('virtualDiskId').get('value')
						virtual_dict['id'] = virtualdisk_id
						virtual_dict['total'] = 0
				
						#for virtual disk size and repo name
						virtualdiskObj = session.get(baseUri+'/VirtualDisk/'+str(virtualdisk_id))
						virtual_disk_size = bytesto(virtualdiskObj.json()['onDiskSize'],'g')
						virtual_dict['size'] = virtual_disk_size
						if  virtualdiskObj.json().get('repositoryId'):
							virtual_dict['repo_name'] = virtualdiskObj.json()['repositoryId']['name']
						if not any(substr in diskname.lower() for substr in exclude_list):
							#for total vm size
							total_size += int(virtual_disk_size)
							virtual_dict['total'] += int(virtual_disk_size)
						virtualist.append(virtual_dict)
				total_usage  += total_size
				res_dict['vm_name']= v['name']
				res_dict['virtualist'] = virtualist
				res_dict['physicalist'] = physicalist
				res_dict['disk_list']  = virtualist+physicalist
				res_dict['total_size'] = total_size
				reslist.append(res_dict)
		return (reslist,total_usage)
	except Exception as e:
		print ("Error  in calculate_size() - " , e)

