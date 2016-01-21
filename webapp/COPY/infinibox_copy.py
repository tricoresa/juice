# ----- Infinibox related modules ----#
import requests
from webapp.utility import bytesto

PAGE_SIZE = '1000'
inf_session = requests.Session()
inf_session.auth=('juice','Svc-ju1c3') # supply auth info
inf_session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
inf_session.verify=False #disables SSL certificate verification

#---- List of servers available in INFINIBOX, param elem can be 'id', or 'name' or 'all' 
#----- the result will be generated respectively with only serverid  list, servernames list, both name,id of servers in a list
def get_serverlist(elem = 'all',serverid = 0):
	# access infinibox to get serverlist
	if serverid >0 :
		infiniUri = 'https://10.62.100.156//api/rest/hosts?id='+str(serverid)+'&page_size='+PAGE_SIZE
	else:
		infiniUri = 'https://10.62.100.156//api/rest/hosts?page_size='+PAGE_SIZE
	infini_list  = inf_session.get(infiniUri)
	infini_list_json = infini_list.json()
	serverlist = []
	for host  in infini_list_json['result']:
		server_dict = {}
		name= host['name']
		id = host['id']
		if elem == "all":
			server_dict['name'] = name
			server_dict['value'] = str(id)
		serverlist.append(server_dict)
		if elem == "name":
			serverlist.append(name)
		if elem == "id":
			serverlist.append(id)
	return serverlist

#---- Given the HOST and Volume list object, it calculates the disk names, disk ids and size of disk for each host  ----# 
def get_infini_report(host_list,volume_list):
	host_list_json=host_list.json()
	volume_list_json = volume_list.json()
	reslist = []
	infini_total_usage = 0
	for host in host_list_json['result']:
		res_dict = {}
		res_dict['servername'] = host['name']
		res_dict['total_size'] = 0
		res_dict['disk_list'] = []
		luns=host['luns']
		for lun in luns:
			for volume in volume_list_json['result']:
				vol_dict = {}
				if volume['type'].upper() == 'MASTER':
					if volume['mapped'] == True:
						if lun['volume_id'] == volume['id']:
							vol_dict['name'] = volume['name']
							vol_dict['id'] = volume['id']
							size = bytesto(volume['size'],'g')
							res_dict['total_size']+= size
							vol_dict['size'] = size
							res_dict['disk_list'].append(vol_dict)
		infini_total_usage += res_dict['total_size']
		reslist.append(res_dict)
	return (reslist,infini_total_usage)

#--- Module accessing the INFINIBOX and fetching all or selected host and volume obj to pass to the get_infini_report()  function for calculation 
#-----returns the result of get_infini_report and total_uage by infinibox(based of selected/ALl hosts)--#
def infini(selected_serverlist,page_size=1000):
	try:
		if page_size == 0:
			page_size = 1000
		serverlist = get_serverlist()
		baseUri='https://10.62.100.156//api/rest/volumes'
		volume_list=inf_session.get(baseUri+"?page_size="+PAGE_SIZE)
		reslist = []
		infini_total_usage = 0
		if selected_serverlist != None:
			if len(selected_serverlist) == 0:
				baseUri='https://10.62.100.156//api/rest/hosts?page_size='+str(page_size)
				host_list=inf_session.get(baseUri)
				host_list_json=host_list.json()
				reslist,infini_total_usage = get_infini_report(host_list,volume_list)
			else:	
				for serverid in selected_serverlist:
					baseUri='https://10.62.100.156//api/rest/hosts?id='+str(serverid)+'&page_size='+str(page_size)
					host_list=inf_session.get(baseUri)
					if (host_list):
						tmplist,total_usage = get_infini_report(host_list,volume_list)
						reslist = reslist+tmplist
						infini_total_usage = infini_total_usage+total_usage
		else:
			pass
		return (reslist,infini_total_usage)
	except Exception as e:
		print ("Error in Infinibox.py - ",e)
