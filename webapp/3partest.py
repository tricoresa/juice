import pprint, json
from hp3parclient import client, exceptions

username='juice'
password='tcs_juice'
vluns=[]

host='10.66.100.6'
cl = client.HP3ParClient("https://%s:8080/api/v1" % host)
cl.login(username, password)
volumes1 = cl.getVolumes()['members']
hosts1 = cl.getHosts()['members']

host2='10.62.100.6'
cl2 = client.HP3ParClient("https://%s:8080/api/v1" % host2)
cl2.login(username, password)
volumes2 = cl2.getVolumes()['members']
hosts2 = cl2.getHosts()['members']

volume_data = volumes1+volumes2
host_data = hosts1+hosts2
for host in hosts1:
        try:
            vluns += cl.getHostVLUNs(host['name'])
        except:
            pass
for host in hosts2:
        try:
            vluns += cl2.getHostVLUNs(host['name'])
        except:
            pass

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