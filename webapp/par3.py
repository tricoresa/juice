import pprint,json
from hp3parclient import client, exceptions
from webapp.utility import bytesto,par3Host_data,par3Volume_data
username='juice'
password='tcs_juice'
host='10.66.100.6'
try:
	cl = client.HP3ParClient("https://%s:8080/api/v1" % host)
	cl.login(username, password)
except Exception as e:
	print (e)
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
		try:
			vluns = cl.getHostVLUNs(server['name'])
			for vl in vluns:
				for vol in par3Volume_data['members']:
					if vl['volumeName'] == vol['name']:
						vol_dict = {}
						vol_dict['id'] = vol['id']
						vol_dict['name'] = vol['name']
						vol_dict['size'] =  bytesto(vol['sizeMiB'],'g')
						vol_dict['WWN'] = vol['wwn']
						res_dict['total_size'] += bytesto(vol['sizeMiB'],'g')
						res_dict['disk_list'].append(vol_dict)
						total_usage += res_dict['total_size']
			reslist.append(res_dict)
		except:
			pass
	cl.logout()
	return reslist, total_usage

def get_3par_serverlist():
	 
	serverlist = []
	for server in par3Host_data['members']:
		server_dict = {}
		server_dict['name'] = server['name']
		server_dict['value'] = str( server['id'])
		serverlist.append(server_dict)
	return serverlist

