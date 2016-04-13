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
   si = SmartConnect(host='10.66.100.15',
                     user='svc-juice',
                     pwd='bnDhPNavNs@^64Y-',
                     port=443,
                     sslContext=context)
   content = si.RetrieveContent()
   result = []
   objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
   for vm in objview.view: 
       repo_dict = {}
       print (vm.runtime.host.name)
       repo_dict['vmhost'] = vm.runtime.host.name
       repo_dict['vmname'] = vm.config.name
       repo_dict['vmware_disklist'] = []
       hardware = vm.config.hardware
       for each_vm_hardware in hardware.device:
         if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
           tmp_dict = {}
           reponame = each_vm_hardware.backing.fileName.split(']')[0] 
           tmp_dict['reponame'] = reponame[1:]
           disk = each_vm_hardware.backing.fileName.split('/')[1]
           tmp_dict['disk'] = disk 
           tmp_dict['capacity'] = each_vm_hardware.capacityInKB/1024/1024
           repo_dict['vmware_disklist'].append(tmp_dict)
       result.append(repo_dict)
   with open('JSON/vmwareCHDC.json', 'w') as outfile:
        json.dump(result, outfile)
if __name__ == "__main__":
   main()

