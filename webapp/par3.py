import pprint,json
from webapp.utility import bytesto,par3Host_data,par3Volume_data,par3Vlun_data
def get_3par(hostlist):
	reslist = []
	total_usage = 0
	serverlist = []

	if len(hostlist)== 0:
		hostlist = par3Host_data['members'] 
	for server in hostlist:
		res_dict = {}
		res_dict['servername']  = server['name']
		res_dict['total_size'] = 0
		res_dict['disk_list'] = []
		vlunlist = []
		try:
			for vlun in par3Vlun_data:
				if vlun['hostname'] == server['name'] and vlun['volumeName'] not in vlunlist:
					vlunlist.append(vlun['volumeName'])
			for vl in vlunlist:
				for vol in par3Volume_data['members']:
					if vl == vol['name']:
						vol_dict = {}
						vol_dict['id'] = vol['id']
						vol_dict['name'] = vol['name']
						vol_dict['size'] =  bytesto(vol['sizeMiB'],'g')
						vol_dict['WWN'] = vol['wwn']
						res_dict['total_size'] += vol_dict['size']#bytesto(vol['sizeMiB'],'g')
						res_dict['disk_list'].append(vol_dict)
			total_usage += res_dict['total_size']
			reslist.append(res_dict)
		except:
			return "Some errror occured in 3par calculation",0
	return reslist, total_usage

def get_3par_serverlist():
	 
	serverlist = []
	for server in par3Host_data['members']:
		server_dict = {}
		server_dict['name'] = server['name']
		server_dict['value'] = str( server['id'])
		serverlist.append(server_dict)
	return serverlist

