# ----- VMware related modules ----#
import requests
from webapp.utility import vmware_data,bytesto

# ------VMware Host List ---- #
def get_vmware_serverlist():
	hostnamelist = []
	for host  in vmware_data:
		hostnamelist.append(host['hostname'])
	return hostnamelist
def get_vmware(hostlist):
	res_dict = {}
	error = ''
	vmware_total_usage = 0
	try:
		if len(hostlist) == 0:
			hostlist = [vmware for vmware in vmware_data]
		for host in hostlist:
			if host['hostname'] not in res_dict:
				res_dict[host['hostname']] = {}
				res_dict[host['hostname']]['total_size'] = 0
				res_dict[host['hostname']]['disk_list'] = []
				for detail in host['vmwareDisk']:
					disk_dict = {}
					disk_dict['repo_name'] = detail['reponame']
					disk_dict['name'] = detail['disk']
					size = bytesto(detail['capacity'],'g')
					disk_dict['size'] = size
					res_dict[host['hostname']]['total_size'] += size
					res_dict[host['hostname']]['disk_list'].append(disk_dict)
					vmware_total_usage += size
				
	except Exception as e:
		error = "Error in VMware calculation - "+str(e)
	return (res_dict,vmware_total_usage,error)
