import pprint,json
from webapp.utility import bytesto,par3Host_data,par3Volume_data,par3Vlun_data
def get_3par(hostlist):
	total_usage = 0
	serverlist = []
	res_dict = {}
	if len(hostlist)== 0:
		hostlist = par3Host_data#['members'] 
	try:
		for server in hostlist:

			if server['name'] not in res_dict:
				res_dict[server['name']] = {}
				res_dict[server['name']]['total_size'] = 0
				res_dict[server['name']]['disk_list'] = []
			vlunlist = []
			for vlun in par3Vlun_data:
				if vlun['hostname'] == server['name'] and vlun['volumeName'] not in vlunlist:
					vlunlist.append(vlun['volumeName'])
			for vl in vlunlist:
				for vol in par3Volume_data: #['members']:
					if vl == vol['name']:
						vol_dict = {}
						vol_dict['id'] = vol['id']
						vol_dict['name'] = vol['name']
						vol_dict['size'] =  bytesto(vol['sizeMiB'],'g')
						vol_dict['WWN'] = vol['wwn']
						res_dict[server['name']]['total_size'] += vol_dict['size']#bytesto(vol['sizeMiB'],'g')
						total_usage += vol_dict['size']
						res_dict[server['name']]['disk_list'].append(vol_dict)
			#total_usage += res_dict[server['name']]['total_size']
	except Exception as e:
		reslist= "Error occured in 3par calculation- "+str(e)
	return res_dict, total_usage

def get_3par_serverlist():
	hostnamelist = []	 
	serverlist = []
	for server in par3Host_data: #['members']:
		if 'name' in server and 'id' in server:
			if server['name'] not in hostnamelist:
				"""server_dict = {}
				server_dict['name'] = server['name']
				server_dict['value'] = str( server['id'])
				serverlist.append(server_dict)"""
				hostnamelist.append(server['name'])
	return hostnamelist

