import pprint, json
from hp3parclient import client, exceptions

username='juice'
password='tcs_juice'
vluns = []
host='10.66.100.6'
cl = client.HP3ParClient("https://%s:8080/api/v1" % host)
cl.login(username, password)
volumes1 = cl.getVolumes()['members']
for vol in volumes1:
    vol['ip']= host
hosts1 = cl.getHosts()['members']
for host in hosts1:
    host['ip'] = host
vluns1 = cl.getVLUNs()['members']
for lun in vluns1:
    lun['ip'] = host

host2='10.62.100.6'
cl2 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
cl2.login(username, password)
volumes2 = cl2.getVolumes()['members']
for vol in volumes2:
    vol['ip']= host2
hosts2 = cl2.getHosts()['members']
for host in hosts2:
    host['ip'] = host2
vluns2 = cl2.getVLUNs()['members']
for lun in vluns2:
    lun['ip'] = host2

host3 = '10.62.100.117'
cl3 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
cl3.login(username, password)
volumes3 = cl3.getVolumes()['members']
for vol in volumes3:
    vol['ip']= host3
hosts3 = cl3.getHosts()['members']
for host in hosts3:
    host['ip'] = host3
vluns3  = cl3.getVLUNs()['members']
for lun in vluns3:
    lun['ip'] = host3

volume_data = volumes1+volumes2+volumes3
host_data = hosts1+hosts2+hosts3
vluns = vluns1+vluns2+vluns3

"""for host in hosts1:
        try:
            vluns += cl.getHostVLUNs(host['name'])
        except:
            pass
for host in hosts2:
        try:
            vluns += cl2.getHostVLUNs(host['name'])
        except:
            pass
for host in hosts3:
	try:
		vluns += cl3.getHostVLUNs(host['name'])
	except:
		pass"""
with open('JSON/3par_vol.json', 'w') as outfile:
        json.dump(volume_data, outfile)
with open('JSON/3par_host.json', 'w') as outfile:
        json.dump(host_data, outfile)

with open('JSON/3par_host.json') as data_file:
        par3Host_data = json.load(data_file)
with open('JSON/3par_vlun.json', 'w') as outfile:
    json.dump(vluns, outfile)
cl.logout()
cl2.logout()
cl3.logout()
