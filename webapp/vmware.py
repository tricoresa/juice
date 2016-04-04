# ----- VMware related modules ----#
import requests
from webapp.utility import vmware_data,bytesto

# ------VMware Host List ---- #
def get_vmware_serverlist():
	vmnamelist = []
	for host  in vmware_data:
		vmnamelist.append(host['vmname'])
	return vmnamelist


def get_unmapped_vmware():
	reslist = []
	error = ''
	try:
		for vmware in vmware_data:
			for details in vmware['vmwareDisk']:
				if details['mounted']== False:
					disk_dict = {}
					disk_dict['repo_name'] = details['reponame']
					disk_dict['name'] = details['disk']
					size = details['capacity']
					disk_dict['size'] = size
					reslist.append(disk_dict)
	except Exception as  e:
		error = "Error in VMware calculation - "+str(e)
	return (reslist,error)
	
		
def get_vmware(vmlist):
	res_dict = {}
	error = ''
	vmware_total_usage = 0
	try:
		if len(vmlist) == 0:
			vmlist = vmware_data # [vmware for vmware in vmware_data]
		for vm in vmlist:
			if vm['vmname'] not in res_dict:
				res_dict[vm['vmname']] = {}
				res_dict[vm['vmname']]['vm_name'] = vm['vmname']
				res_dict[vm['vmname']]['total_size'] = 0
				res_dict[vm['vmname']]['disk_list'] = []
				for detail in vm['vmware_disklist']:
					disk_dict = {}
					disk_dict['repo_name'] = detail['reponame']
					disk_dict['name'] = detail['disk']
					disk_dict['source'] =  'VMware'
					size = detail['capacity']
					disk_dict['size'] = size
					res_dict[vm['vmname']]['total_size'] += size
					res_dict[vm['vmname']]['disk_list'].append(disk_dict)
					vmware_total_usage += size
	except Exception as e:
		error = "Error in VMware calculation - "+str(e) 
	return (res_dict,vmware_total_usage,error)
