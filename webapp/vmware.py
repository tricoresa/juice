# ----- VMware related modules ----#
import requests,math,json
from webapp.utility import bytesto
# ------VMware unique VM  List ---- #
def get_vmware_serverlist():
	with open('webapp/JSON/vmware.json') as data_file:
		print ('vmware_serverlist')
		vmware_data = json.load(data_file)
	vmnamelist = []
	for host  in vmware_data:
		vmnamelist.append(host['vmname'])
	return vmnamelist

# ------ List of unmapped virtual machines------ #
def get_unmapped_vmware():
	reslist = []
	error = ''
	try:
		with open('webapp/JSON/vmware.json') as data_file:
			print ('unmapped_vmware')
			vmware_data = json.load(data_file)
		for vmware in vmware_data:
			if vmware['vmhost'] == '' or vmware['vmhost'] == None:
				#if vmware['ip'] not  in resdict:
				resdict = {}
				resdict[vmware['ip']] = {}
				resdict[vmware['ip']]['source'] = 'VMware'
				resdict[vmware['ip']]['total_size']= 0
				resdict[vmware['ip']]['disk_list']
				vm_dict = {}
				vm_dict['name'] = vmware['vmname']
				capacity  = 0
				for detail in vmware['vmware_disklist']:
					vm_dict['repo'] = detail['reponame']
					capacity += detail['capacity']
				vm_dict['size'] = math.ceil(capacity)
				resdict[vmware['ip']]['total_size'] += capacity
				resdict[vmware['ip']]['disk_list'].append(vm_dict)
				reslist.append(resdict)
	except Exception as  e:
		error = "Error in VMware calculation - "+str(e)
	return (reslist,error)
	
# ---- List out the VM and its disk/repo details on the basis of selected list of VMs ---- #		
def get_vmware(vmlist):
	error = ''
	reslist = []
	vmware_total_usage = 0
	try:
		with open('webapp/JSON/vmware.json') as data_file:
			print ('get_vmware')
			vmware_data = json.load(data_file)
		if len(vmlist) == 0:
			vmlist = vmware_data # [vmware for vmware in vmware_data]
		for vm in vmlist:
			if 'vmname' in vm:
				res_dict = {}
				temp_dict = {}
				#if  vm['vmname'] not in res_dict:
				res_dict[vm['vmname']] = {}
				res_dict[vm['vmname']]['source'] = 'VMware'
				res_dict[vm['vmname']]['vmhost'] = vm['vmhost']
				res_dict[vm['vmname']]['vm_name'] = vm['vmname']
				res_dict[vm['vmname']]['total_size'] = 0
				res_dict[vm['vmname']]['disk_list'] = []
				for detail in vm['vmware_disklist']:
					if detail['reponame'] not in temp_dict:
						temp_dict[detail['reponame']] = []
					#------- remove duplicate disk and repo combination occurence in the vmware report
					if detail['disk'] not in  temp_dict[detail['reponame']]:
						temp_dict[detail['reponame']].append(detail['disk'])
					disk_dict = {}
					disk_dict['repo_name'] = detail['reponame']
					disk_dict['name'] = detail['disk']
					disk_dict['source'] =  'VMware'
					size = math.ceil(detail['capacity'])
					disk_dict['size'] = size
					#disk_dict['used_size']= math.ceil(detail['used_size'])
					res_dict[vm['vmname']]['total_size'] += size
					res_dict[vm['vmname']]['disk_list'].append(disk_dict)
					vmware_total_usage += size
				if vm['vmname'] not in res_dict and len(res_dict[vm['vmname']]['disk_list']) == 0:
					res_dict.pop(vm['vmname'],None)
				reslist.append(res_dict)
	except Exception as e:
		print (e)
		error = "Error in VMware calculation - "+str(e) 
	return (reslist,math.ceil(vmware_total_usage),error)
