# ----- VMware related modules ----#
import requests,math
from webapp.utility import vmware_data,bytesto

# ------VMware unique VM  List ---- #
def get_vmware_serverlist():
	vmnamelist = []
	for host  in vmware_data:
		vmnamelist.append(host['vmname'])
	return vmnamelist

# ------ List of unmapped virtual machines------ #
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
	
# ---- List out the VM and its disk/repo details on the basis of selected list of VMs ---- #		
def get_vmware(vmlist):
	res_dict = {}
	error = ''
	vmware_total_usage = 0
	temp_dict = {}
	try:
		if len(vmlist) == 0:
			vmlist = vmware_data # [vmware for vmware in vmware_data]
		for vm in vmlist:
			if 'vmname' in vm:
				if  vm['vmname'] not in res_dict:
					res_dict[vm['vmname']] = {}
					res_dict[vm['vmname']]['source'] = 'VMware'
					res_dict[vm['vmname']]['vmhost'] = vm['vmhost']
					res_dict[vm['vmname']]['vm_name'] = vm['vmname']
					res_dict[vm['vmname']]['total_size'] = 0
					res_dict[vm['vmname']]['disk_list'] = []
				for detail in vm['vmware_disklist']:
					if detail['reponame'] not in temp_dict:
						temp_dict[detail['reponame']] = []
					#-------- remove duplicate disk and repo combination occurence in the vmware report
					if detail['disk'] not in  temp_dict[detail['reponame']]:
						temp_dict[detail['reponame']].append(detail['disk'])
						disk_dict = {}
						disk_dict['repo_name'] = detail['reponame']
						disk_dict['name'] = detail['disk']
						disk_dict['source'] =  'VMware'
						size = math.ceil(detail['capacity'])
						disk_dict['size'] = size
						res_dict[vm['vmname']]['total_size'] += size
						res_dict[vm['vmname']]['disk_list'].append(disk_dict)
						vmware_total_usage += size
				if vm['vmname'] not in res_dict and len(res_dict[vm['vmname']]['disk_list']) == 0:
					res_dict.pop(vm['vmname'],None)
	except Exception as e:
		error = "Error in VMware calculation - "+str(e) 
	return (res_dict,math.ceil(vmware_total_usage),error)
