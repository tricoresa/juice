#!/usr/bin/env python
from __future__ import print_function
import sys,json
sys.path.append("/u01/juice/Django_juice/pyvmomi-community-samples/samples")
from samples import getallvms
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import argparse
import atexit
import getpass
import ssl


def main():
   """
   Simple command-line program for listing the virtual machines on a system.
   """
   context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
   context.verify_mode = ssl.CERT_NONE
   si = SmartConnect(host='10.62.100.15',#'chdcvcent01.tricorems.com',
                     user='svc-juice',
                     pwd='bnDhPNavNs@^64Y-',
                     port=int(443),
                     sslContext=context)
   content = si.RetrieveContent()
   result = []
   objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
   for vm in objview.view: 
       repo_dict = {}
       repo_dict['vmhost'] = vm.runtime.host.name or ''
       repo_dict['ip'] =  '10.62.100.15'
       repo_dict['vmname'] = vm.config.name
       try:
         vm_usage = vm.resourcePool.summary.quickStats.guestMemoryUsage 
         repo_dict['vm_usage'] = vm_usage/1024
         vm_reserved = vm.resourcePool.summary.runtime.memory.reservationUsedForVm 
         repo_dict['vm_reserved']=vm_reserved/1024/1024
       except:
         pass
       repo_dict['vmware_disklist'] = []

       for device in vm.config.hardware.device:
            if (device.key >= 2000) and (device.key < 3000):
               tmp_dict = {}
               if hasattr(device.backing, 'fileName'):
                   tmp_dict = {}
                   datastore = device.backing.datastore
                   #print  (device)
                   if datastore:
                       tmp_dict['reponame'] = datastore.name
                       tmp_dict['capacity']  = device.capacityInKB/1024/1024 # converting bytes to GB
                       #tmp_dict['used_size'] = (datastore.summary.capacity - datastore.summary.freeSpace)/1024/1024/1024
                       tmp_dict['disk'] = device.backing.fileName.split('/')[1]
               else:
                    tmp_dict['reponame'] = ''
                    tmp_dict['disk'] = ''
                    tmp_dict['capacity']= 0
                    tmp_dict['used_size'] = 0
               repo_dict['vmware_disklist'].append(tmp_dict)
       result.append(repo_dict)


       """for each_vm_hardware in hardware.device:
         if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
           tmp_dict = {}
           try:
               reponame = each_vm_hardware.backing.fileName.split(']')[0] 
               tmp_dict['reponame'] = reponame[1:]
               disk = each_vm_hardware.backing.fileName.split('/')[1]
               tmp_dict['capacity'] = each_vm_hardware.capacityInKB/1024/1024
               tmp_dict['disk'] = disk
           except:
               tmp_dict['reponame'] = ''
               tmp_dict['disk'] = '' 
               tmp_dict['capacity']= 0
           repo_dict['vmware_disklist'].append(tmp_dict)
       result.append(repo_dict)"""

   si = SmartConnect(host='10.66.100.15',
                     user='svc-juice',
                     pwd='bnDhPNavNs@^64Y-',
                     port=int(443),
                     sslContext=context)
   content = si.RetrieveContent()
   objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
   for vm in objview.view:
       repo_dict = {}
       repo_dict['vmhost'] = vm.runtime.host.name or ''
       repo_dict['ip'] = '10.66.100.15' 
       repo_dict['vmname'] = vm.config.name
       try:
         vm_usage = vm.resourcePool.summary.quickStats.guestMemoryUsage
         repo_dict['vm_usage'] = vm_usage/1024
         vm_reserved = vm.resourcePool.summary.runtime.memory.reservationUsedForVm
         repo_dict['vm_reserved']=vm_reserved/1024/1024
       except:
         pass
       repo_dict['vmware_disklist'] = []
       
       for device in vm.config.hardware.device:
            if (device.key >= 2000) and (device.key < 3000):
               tmp_dict = {}
               if hasattr(device.backing, 'fileName'):
                   tmp_dict = {}
                   datastore = device.backing.datastore
                   if datastore:
                       tmp_dict['reponame'] = datastore.name
                       tmp_dict['capacity']  = device.capacityInKB/1024/1024 # converting bytes to GB
                       #tmp_dict['used_size'] = (datastore.summary.capacity - datastore.summary.freeSpace)/1024/1024/1024
                       tmp_dict['disk'] = device.backing.fileName.split('/')[1]
               else:
                    tmp_dict['reponame'] = ''
                    tmp_dict['disk'] = ''
                    tmp_dict['capacity']= 0
                    tmp_dict['used_size'] = 0
               repo_dict['vmware_disklist'].append(tmp_dict)
       result.append(repo_dict)
       
       """for each_vm_hardware in hardware.device:
         if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
           tmp_dict = {}
           try:
               reponame = each_vm_hardware.backing.fileName.split(']')[0]
               tmp_dict['reponame'] = reponame[1:]
               disk = each_vm_hardware.backing.fileName.split('/')[1]
               tmp_dict['disk'] = disk
               tmp_dict['capacity']= each_vm_hardware.capacityInKB/1024/1024 
           except:
               tmp_dict['reponame'] = ''  
               tmp_dict['disk'] = ''
               tmp_dict['capacity'] =  0
           repo_dict['vmware_disklist'].append(tmp_dict)
       result.append(repo_dict)"""

   with open('JSON/vmware.json', 'w') as outfile:
        json.dump(result, outfile)
if __name__ == "__main__":
   main()

