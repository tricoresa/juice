# ----- VMware related modules ----#
import requests,math
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
			if vmware['vmhost'] == '':
				vm_dict = {}
				vm_dict['name'] = vmware['vmname']
				capacity  = 0
				for detail in vmware['vmware_disklist']:
					capacity += detail['capacity']
				vm_dict['size'] = math.ceil(capacity)
				reslist.append(vm_dict)
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
				res_dict[vm['vmname']]['VMware'] = 1
				res_dict[vm['vmname']]['vmhost'] = vm['vmhost']
				res_dict[vm['vmname']]['vm_name'] = vm['vmname']
				res_dict[vm['vmname']]['total_size'] = 0
				res_dict[vm['vmname']]['disk_list'] = []
				for detail in vm['vmware_disklist']:
					disk_dict = {}
					disk_dict['repo_name'] = detail['reponame']
					disk_dict['name'] = detail['disk']
					disk_dict['source'] =  'VMware'
					size = detail['capacity']
					disk_dict['size'] = math.ceil(size)
					res_dict[vm['vmname']]['total_size'] += size
					res_dict[vm['vmname']]['disk_list'].append(disk_dict)
					vmware_total_usage += size
	except Exception as e:
		error = "Error in VMware calculation - "+str(e) 
	return (res_dict,vmware_total_usage,error)
