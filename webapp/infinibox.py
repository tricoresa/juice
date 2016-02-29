# ----- Infinibox related modules ----#
import requests
from webapp.utility import infini_host_data,bytesto,infini_volume_data

# ------Infinibox Server List ---- #
def get_infini_serverlist():
	serverlist = []
	for host  in infini_host_data['result']:
		server_dict = {}
		name= host['name']
		id = host['id']
		server_dict['name'] = name
		server_dict['value'] = str(id)
		serverlist.append(server_dict)
	return serverlist

#---- Given the HOST and Volume list object, it calculates the disk names, disk ids and size of disk for each host  ----# 
def get_infini(hostlist,limit=1000):
        volume_list_json = infini_volume_data
        reslist = []
        infini_total_usage = 0
        try:
                if  len(hostlist) == 0:
                        hostlist = infini_host_data['result']
                for host in hostlist:
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
        except Exception as e:
                reslist = "Error in Infinibox calculation - "+str(e)
        return (reslist,infini_total_usage)

