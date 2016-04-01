import pprint, json
from hp3parclient import client, exceptions

username='juice'
password='tcs_juice'
vluns = []
host='10.66.100.6'
cl = client.HP3ParClient("https://%s:8080/api/v1" % host)
cl.login(username, password)
volumes1 = cl.getVolumes()['members']
hosts1 = cl.getHosts()['members']
vluns1 = cl.getVLUNs()['members']

host2='10.62.100.6'
cl2 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
cl2.login(username, password)
volumes2 = cl2.getVolumes()['members']
hosts2 = cl2.getHosts()['members']
vluns2 = cl2.getVLUNs()['members']

host3 = '10.62.100.117'
cl3 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
cl3.login(username, password)
volumes3 = cl3.getVolumes()['members']
hosts3 = cl3.getHosts()['members']
vluns3  = cl3.getVLUNs()['members']

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
