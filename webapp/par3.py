import pprint,json
from webapp.utility import bytesto
# -----Get list of unmapped 3 Par volumes ----#
def get_unmapped_3par():
	with open('webapp/JSON/3par_vol.json') as data_file:
		print ('par3_unmapped')
		par3Volume_data = json.load(data_file)
	with open('webapp/JSON/3par_vlun.json') as data_file:
		par3Vlun_data = json.load(data_file)
	error = ''
	resdict = {}
	try:
		vol_list = []
		vlun_wwnlist = []
		for vl in par3Vlun_data:
			if vl['volumeWWN'] not in vlun_wwnlist:
				vlun_wwnlist.append(vl['volumeWWN'])
		for vol in par3Volume_data:
			if vol['wwn'] not in  vlun_wwnlist and vol['wwn'] not in vol_list:
				vol_list.append(vol['wwn'])
				if vol['ip'] not in resdict:
					resdict[vol['ip']] = {}
					resdict[vol['ip']]['source'] = '3par'
					resdict[vol['ip']]['total_size'] = 0
					resdict[vol['ip']]['disk_list'] = []
				vol_dict = {}
				vol_dict['id'] = vol['id']
				vol_dict['name'] = vol['name']
				size = bytesto(vol['sizeMiB'],'k')
				vol_dict['size'] =  str(size)
				vol_dict['WWN'] = vol['wwn']
				resdict[vol['ip']]['total_size'] += size
				resdict[vol['ip']]['disk_list'].append(vol_dict)
	except Exception as e:
		error = str(e)
	return resdict,error

# ------ List of 3par volumes and respective luns on the basis of selected list of 3par hosts ----- #				
def get_3par(hostlist):
	total_usage = 0
	error = ''
	serverlist = []
	vol_list = []
	res_dict = {}
	with open('webapp/JSON/3par_host.json') as data_file:
		print ('get_par3')
		par3Host_data = json.load(data_file)
	with open('webapp/JSON/3par_vol.json') as data_file:
		par3Volume_data = json.load(data_file)
	with open('webapp/JSON/3par_vlun.json') as data_file:
		par3Vlun_data = json.load(data_file)

	if len(hostlist)== 0:
		hostlist = par3Host_data#['members'] 
	try:
		for server in hostlist:
			if 'name' in server:
				vlunlist = []
				for vlun in par3Vlun_data:
					if 'hostname' in vlun and vlun['hostname'] == server['name'] and vlun['volumeName'] not in vlunlist:
						vlunlist.append(vlun['volumeName'])
				if len(vlunlist) > 0:
					if server['name'] not in res_dict:
						res_dict[server['name']] = {}
						res_dict[server['name']]['source'] = '3Par'
						res_dict[server['name']]['volume_list'] = []
						res_dict[server['name']]['total_size'] = 0
						res_dict[server['name']]['disk_list'] = []	
				for vl in vlunlist:
					for vol in par3Volume_data: #['members']:
						if vl == vol['name'] and vol['name'] not in res_dict[server['name']]['volume_list'] and vol['id'] not in vol_list:
							vol_list.append(vol['id']) # eliminating duplicate volumes from 3par report
							res_dict[server['name']]['volume_list'].append(vol['name'])
							vol_dict = {}
							vol_dict['id'] = vol['id']
							vol_dict['name'] = vol['name']
							vol_dict['source'] = '3Par'
							size = bytesto(vol['sizeMiB'],'k')
							vol_dict['size'] =  size
							vol_dict['WWN'] = vol['wwn']
							res_dict[server['name']]['total_size'] += size #bytesto(vol['sizeMiB'],'g')
							total_usage += size
							res_dict[server['name']]['disk_list'].append(vol_dict)
				if server['name'] in res_dict and len(res_dict[server['name']]['disk_list']) == 0:
					res_dict.pop(server['name'],None) 
	except Exception as e:
		error = "Error occured in 3par calculation- "+str(e)
	return res_dict, total_usage, error

# ------List of 3par Hosts ---------- #
def get_3par_serverlist():
	hostnamelist = []	 
	serverlist = []
	with open('webapp/JSON/3par_host.json') as data_file:
		print ('par3 serverlist')
		par3Host_data = json.load(data_file)

	for server in par3Host_data: #['members']:
		if 'name' in server and 'id' in server:
			if server['name'] not in hostnamelist:
				"""server_dict = {}
				server_dict['name'] = server['name']
				server_dict['value'] = str( server['id'])
				serverlist.append(server_dict)"""
				hostnamelist.append(server['name'])
	return hostnamelist

