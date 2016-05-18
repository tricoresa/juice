# ----- Infinibox related modules ----#
import requests,json
from webapp.utility import bytesto

# ------Infinibox Server List ---- #
def get_infini_serverlist():
	serverlist = []
	hostnamelist = []
	with open('webapp/JSON/infini_host.json') as data_file:
		print ('infinibox serverlist')
		infini_host_data = json.load(data_file)

	for host  in infini_host_data: #['result']:
		#server_dict = {}
		name= host['name']
		id = host['id']
		if name not in hostnamelist:
			"""server_dict['name'] = name
			server_dict['value'] = str(id)
			serverlist.append(server_dict)
			"""
			hostnamelist.append(name)
	return hostnamelist

# ------ Listing the unmapped volumes in infinibox ---- #
def get_unmapped_infini():
	with open('webapp/JSON/infini_vol.json') as data_file:
		print ('unmapped_infini')
		infini_volume_data = json.load(data_file)
	volume_list_json = infini_volume_data
	error = ''
	resdict = {}
	try:
			for volume in volume_list_json:	
				if volume['mapped'] == False:
					if 'ip' in volume and volume['ip'] not in resdict:
						resdict[volume['ip']] = {}
						resdict[volume['ip']]['source'] = 'Infinibox'
						resdict[volume['ip']]['total_size'] = 0
						resdict[volume['ip']]['disk_list'] = []
					vol_dict = {}
					vol_dict['name'] = volume['name']
					vol_dict['id'] = volume['id']
					size = bytesto(volume['size'],'g')
					vol_dict['size'] = size
					resdict[volume['ip']]['total_size'] += size
					resdict[volume['ip']]['disk_list'].append(vol_dict)		
	except  Exception as e:
		error = "Error in Infinibox calculation - "+str(e)
	return (resdict,error)

#---- Given the HOST and Volume list object, it calculates the disk names, disk ids and size of disk for each host  ----# 
def get_infini(hostlist,limit=1000):
        with open('webapp/JSON/infini_vol.json') as data_file:
                print ('get_infini')
                infini_volume_data = json.load(data_file)
        volume_list_json = infini_volume_data
        infini_total_usage = 0
        error = ''
        res_dict = {}
        vol_list = []
        try:
                if  len(hostlist) == 0:
                        hostlist = infini_host_data #['result']
                for host in hostlist:
                    if 'luns' in host:
                        if 'name' in host and host['name'] not in res_dict:
                            res_dict[ host['name']] = {}
                            res_dict[ host['name']]['source'] = 'Infinibox'
                            res_dict[host['name']]['total_size'] = 0
                            res_dict[host['name']]['disk_list'] = []
                        luns=host['luns']
                        for lun in luns:
                            for volume in volume_list_json: #['result']:
                                   vol_dict = {}
                                   if lun['volume_id'] == volume['id'] and volume['mapped'] == True: 
                                       if volume['id'] not in vol_list:
                                           vol_list.append(volume['id'])  # eliminating duplicate columes from infini report
                                           vol_dict['name'] = volume['name']
                                           vol_dict['id'] = volume['id']
                                           vol_dict['source'] = 'Infinibox'
                                           size = bytesto(volume['size'],'g')
                                           res_dict[host['name']]['total_size']+= size
                                           #infini_total_usage += size
                                           vol_dict['size'] = size
                                           res_dict[host['name']]['disk_list'].append(vol_dict)
                        infini_total_usage += res_dict[host['name']]['total_size']
                        if host['name'] in res_dict and len(res_dict[host['name']]['disk_list']) == 0:
                            res_dict.pop(host['name'],None)
        except Exception as e:
                error = "Error in Infinibox calculation - "+str(e)
        return (res_dict,infini_total_usage,error)

