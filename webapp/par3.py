import pprint,json
from webapp.utility import bytesto,par3Host_data,par3Volume_data,par3Vlun_data
def get_unmapped_3par():
	error = ''
	reslist = []
	try:
		vlun_wwnlist = []
		for vl in par3Vlun_data:
			vlun_wwnlist.append(vl['volumeWWN'])
		for vol in par3Volume_data:
			if vol['wwn'] not in  vlun_wwnlist:
				vol_dict = {}
				vol_dict['id'] = vol['id']
				vol_dict['name'] = vol['name']
				size = bytesto(vol['sizeMiB'],'k')
				vol_dict['size'] =  str(size)+' gb'
				vol_dict['WWN'] = vol['wwn']
				reslist.append(vol_dict)
	except Exception as e:
		error = str(e)
	print ('3par - ',len(reslist))
	return reslist,error
				
def get_3par(hostlist):
	total_usage = 0
	error = ''
	serverlist = []
	res_dict = {}
	if len(hostlist)== 0:
		hostlist = par3Host_data#['members'] 
	try:
		for server in hostlist:
			if 'name' in server:
				if server['name'] not in res_dict:
					res_dict[server['name']] = {}
					res_dict[server['name']]['volume_list'] = []
					res_dict[server['name']]['total_size'] = 0
					res_dict[server['name']]['disk_list'] = []
				vlunlist = []
				for vlun in par3Vlun_data:
					if 'hostname' in vlun and vlun['hostname'] == server['name'] and vlun['volumeName'] not in vlunlist:
						vlunlist.append(vlun['volumeName'])
				for vl in vlunlist:
					for vol in par3Volume_data: #['members']:
						if vl == vol['name'] and vol['name'] not in res_dict[server['name']]['volume_list']:
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
			#total_usage += res_dict[server['name']]['total_size']
	except Exception as e:
		error = "Error occured in 3par calculation- "+str(e)
	return res_dict, total_usage, error

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

