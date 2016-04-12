from django.shortcuts import render
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from webapp.models import JuiceGroupnames,JuiceGroupvm
import json,csv,collections
from django.utils.encoding import smart_str
from webapp.utility import *
from webapp.infinibox import *
from webapp.par3 import *
from webapp.vmware import *
from django.views.generic.base import View
from django.shortcuts import render,get_object_or_404,redirect
from collections import OrderedDict
# ***************************************************
#Intro - Vmreport allows the user to have a detailed view of all the VM/Server(from OVM/Infinibox)
#which are registered in a customer group, based on the available filters on the VMreport."""
# ***************************************************

#------ vm/disk report common module -------#
def get_result_usage(cust_acronym=[],server = [], server_acronym = ''):
        result = []
        usage = 0
        error = []
        hostlist  = applyfilter(cust_acronym,server,server_acronym)
        if len(hostlist)>0:
            infini_result,infini_usage,infini_error = get_infini(hostlist)
            ovm_result,ovm_usage,ovm_error = get_ovm(hostlist)
            vmware_result,vmware_usage,vmware_error = get_vmware(hostlist)
            par3_result,par3_usage,par3_error = get_3par(hostlist)
 
            result.append(ovm_result)
            result.append(infini_result)
            result.append(par3_result)
            result.append(vmware_result)
            res_dict = {}
            for res in result:
                for key,value in res.items():
                    if key not in res_dict:
                        res_dict[key] = {'disk_list':[],'total_size':0}
                    res_dict[key]['disk_list']+= res[key]['disk_list']
                    res_dict[key]['total_size'] += res[key]['total_size']
            usage = ovm_usage+infini_usage+par3_usage+vmware_usage

            if len(ovm_error) > 0:
                 error.append(ovm_error) 
            if len(infini_error) > 0:
                error.append(infini_error)
            if len(par3_error)>0:
                error.append(par3_error)
            if len(vmware_error)>0:
                error.append(vmware_error)
        else:
            res_dict,usage,error = {},0,''
        return res_dict,usage,error

# ------ Module for unmapped Disks and VM listing  --------#
class UnmappedDisk(View):	
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		error_msg = ''
		res_dict = {}
		res_list = []
		active_user = get_user_grp(request.user)
		ovm_disk_list,error = get_unmapped_ovm()
		res_dict['OVM'] = ovm_disk_list
		infini_disk_list,error_msg = get_unmapped_infini()
		res_dict ['infinibox'] = infini_disk_list
		par3_disk_list,error = get_unmapped_3par()
		res_dict['par3'] = par3_disk_list
		vmware_disk_list,error_msg= get_unmapped_vmware()
		res_dict['vmware'] = vmware_disk_list
		res_list.append(res_dict)
		return render(request,'webapp/unmapped.html',{'active_user':active_user,'error_msg':error_msg,'res_list':res_list,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})		

#---- Summary page lists out all the customer groups with the total disk usage.---#
class Summary(View):
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		grp_list = []
		active_user = get_user_grp(request.user)
		groupObj = None
		pagination_res = None
		error_msg = ''
		customergrouplist = JuiceGroupnames.objects.all().order_by('name')
		selected_grpid = int(self.request.GET.get('group_filter') or 0)
		if selected_grpid > 0:
			groupObj = JuiceGroupnames.objects.filter(groupnameid=selected_grpid).order_by('name')
		else:
			groupObj = JuiceGroupnames.objects.all().order_by('name')
		page = int(self.request.GET.get('page') or 1)
		limit =int(self.request.GET.get('limit') or 20)
		pagination_res = pagination(groupObj,limit,page)
		
		try:
			for customer in pagination_res:
				res_dict =  {}
				res_dict['hostidlist'] = []	
				res_dict['physical_disk_size'] = 0
				res_dict['virtual_disk_size'] = 0
				res_dict ['size'] = 0  
				total_grp_usage = 0
				res_dict['groupname']  = customer.name
				res_dict['groupid'] = customer.groupnameid
				cust_acronym =  customer.acronym.split(',')
				vlist = applyfilter(cust_acronym)
				if len(vlist) >  0:
					# ------- Processing OVM result
					ovm_res,ovm_usage,error = get_ovm(vlist)
					for key, elem in ovm_res.items():
						if len(elem.get('virtualist')) > 0 :
							for vm_json in elem['virtualist']:
								res_dict['virtual_disk_size'] += vm_json['total']
						if len(elem.get('physicalist')) > 0:
							for vm_json in elem['physicalist']:
								res_dict['physical_disk_size'] += vm_json['total']
					# ------------- Processing Infini result
					infini_res,infini_usage,error = get_infini(vlist,limit)
					for key,res in infini_res.items():
						for elem in res.get('disk_list'):
							res_dict['physical_disk_size'] += elem['size']
							res_dict['size'] += elem['size']
					
					# ------------ Processing par3 result
					par3_result,par3_usage,error = get_3par(vlist)
					for key,res in par3_result.items():
						for elem in res.get('disk_list'):
							res_dict['physical_disk_size'] += elem['size']
							res_dict['size'] += elem['size']
					
					# ---------- Processing vmware result
					vmware_result,vmware_usage,error= get_vmware(vlist)
					for key,res in vmware_result.items():
						for elem in res.get('disk_list'):
							res_dict['virtual_disk_size'] += elem['size']
					res_dict['size'] = res_dict['virtual_disk_size']+res_dict['physical_disk_size']
				grp_list.append(res_dict)
		except Exception as e:
			error_msg = "Exception handled in Summary module - ",e


		return render(request,'webapp/summary.html',{'active_user':active_user,'error_msg':error_msg,'grp_list':grp_list,'customergrouplist':customergrouplist,'selected_grpid':selected_grpid,'pagination':pagination_res,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

#----------------Module to export the VM/Disk report ---------------#
class CSVExport(View):
	def post(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		ajax = int(self.request.POST.get('ajax') or 0)
		resdict = json.loads(self.request.POST.get('resdict'))
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=VMReport.csv'
		writer = csv.writer(response, csv.excel)
		response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
		writer.writerow([
			smart_str('VM Name'),
			smart_str('Server Name'),
			smart_str('Repo Name'),
			smart_str('Disk Id'),
			smart_str('Disk Name'),
			smart_str('Disk Size'),
		])
		result = []
		for key,val in resdict.items():
			for disk in val['disk_list']:
				res_dict = {}
				res_dict['repo'] = disk.get('repo_name')
				res_dict['diskid'] = disk.get('id')
				res_dict['diskname'] = disk.get('name')
				res_dict['disksize'] = disk.get('size')
				res_dict['vm'] = val.get('vm_name')
				res_dict['servername'] = key if val.get('VMware') != 1 else val.get('vmhost')
				result.append(res_dict)
		for obj in result:
			writer.writerow([
				smart_str(obj['vm']),
				smart_str(obj['servername']),
				smart_str(obj['repo']),
				smart_str(obj['diskid']),
				smart_str(obj['diskname']),
				smart_str(obj['disksize']),
			])
		return response
		
#----Dashboard is th VM report where Vm from OVM and disks from INfinibox and 3par are listed with respective repo name, disk name ,disk size
class Dashboard(View):
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)	
		custgrp = int(self.request.GET.get('group') or 0)
		cust_grplist = JuiceGroupnames.objects.all().order_by('name')
		ovm_serverlist = get_ovm_serverlist()
		infini_serverlist = get_infini_serverlist()
		par3_serverlist = get_3par_serverlist()
		vmware_serverlist = get_vmware_serverlist()
		serverlist = ovm_serverlist + infini_serverlist + par3_serverlist+vmware_serverlist
		newserverlist = set(serverlist )
		result = []
		total_usage  = 0
		return render(request,'webapp/dashboard.html',{'exclude_list':exclude_list,'error_notify':'','reslist':result,'active_user':active_user,'serverlist':newserverlist,'cust_grp':custgrp,'customergrouplist':cust_grplist,'total_usage':total_usage,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})	
	def post(self,request):

		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		custgrp = int(self.request.POST.get('group') or 0)
		server = self.request.POST.getlist('server') or []
		server_acronym = self.request.POST.get('server_acronym') or ''
		cust_grplist = JuiceGroupnames.objects.all().order_by('name')
		result=[]
		total_usage = 0
		error_notify = ''
		empty_notify  = ''
		newserverlist = []
		cust_acronym = []
		res_dict = {}
		try:
			if custgrp > 0:
				cust_acronym = JuiceGroupnames.objects.get(groupnameid = custgrp).acronym 
				cust_acronym = cust_acronym.split(',') # handling multiple group acronyms
			#else:
			#	custgrp_obj = JuiceGroupnames.objects.all()
			#	for cust in custgrp_obj:
			#		acronymlist = cust.acronym.split(',') # handling multiple group acronyms
			#		for acronym in acronymlist:
			#			cust_acronym.append(acronym)
			hostidlist = []
			ovm_serverlist = get_ovm_serverlist()
			infini_serverlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmware_serverlist = get_vmware_serverlist()
			serverlist = ovm_serverlist + infini_serverlist + par3_serverlist + vmware_serverlist
			newserverlist = set(serverlist)
			
			if active_user == 1 :
				res_dict,usage,error = get_result_usage(cust_acronym,server,server_acronym)	
			else:
				res_dict,usage,error = get_result_usage(cust_acronym)
			total_usage = usage
			if len(error)  > 0:
				error_notify = str(error)
			if len(res_dict) == 0:
				if custgrp == 0:
					pass
				else:
					empty_notify = "No result matching the filters"
		except Exception as e:
			error_notify = "Error in Report caluclation - "+str(e)
		return render(request,'webapp/dashboard.html',{'error_notify':error_notify,'empty_notify':empty_notify,'resdict_csv':res_dict,'exclude_list':exclude_list,'resdict':OrderedDict(sorted(res_dict.items(), key=lambda t: t[0])),'active_user':active_user,'serverlist':newserverlist,'cust_grp':custgrp,'customergrouplist':cust_grplist,'total_usage':total_usage,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	
	
# -----  Repository Report to list out the OVM repositories with their total size, used size and free space ---#
class Repository(View):
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		reslist = []
		repolist = []
		error_msg = ''
		selected_repoid = self.request.GET.get('repo') or ''
		try:
			for repo in repodata:
				repolist.append(repo['id'])
			if selected_repoid != '':
				res_dict = get_repo_detail(selected_repoid)
				reslist.append(res_dict)
			else:
				for repo in repolist:
					repoid = repo['value']
					res_dict = get_repo_detail(repoid)
					reslist.append(res_dict)
		except Exception as e:
			print ("Repository Module error - ",e)
			error_msg = "Exception handled in Repository Module"
		return render(request,'webapp/repository.html',{'active_user':active_user,'error_msg':error_msg,'reslist':reslist,'selected_repoid':selected_repoid,'repolist':repolist,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

# ------Report of customer groups with the name of VM/servers grouped in each, EDIT/DELETE function available on customer group list ---#
class CustomerGroupList(View):
	def post (self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		reslist = []
		active_user = get_user_grp(request.user)
		pagination_res = None
		success_msg = ''
		error_msg = ''
		delete_grp = int(self.request.POST.get('delete_grp') or 0)
		delete_grpid = self.request.POST.getlist('check[]') or []
		page = int(self.request.POST.get('page') or 1)
		limit =int(self.request.POST.get('limit') or 20)
		try:
			if delete_grp == 1:
				for grpid in delete_grpid:
					x = JuiceGroupnames.objects.filter(groupnameid = grpid).delete()
					y = JuiceGroupvm.objects.filter(groupid = grpid).delete()
					success_msg = "Group deleted successfully"
			groupObj = JuiceGroupnames.objects.all().order_by('name')
			pagination_res = pagination(groupObj,limit,page)
			for customer in pagination_res:
				res_dict =  {}
				res_dict['customergrp_id'] = customer.groupnameid
				res_dict['customername']  = customer.name
				vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
				hostidlist = []
				for vm in vmgroupobj:
					hostidlist.append(vm.vm)
				#ovm_vmlist, infini_serverlist ,par3_serverlist= get_servernames('',hostidlist)
				res_dict['vmlist'] =set(hostidlist)# ovm_vmlist+infini_serverlist+par3_serverlist)
				reslist.append(res_dict)
		except Exception as e:
			print ("Customer Grouplist error - ",e)
			error_msg = "Exception handled in Customer group list"

		return render(request,'webapp/customer_grplist.html',{'active_user':active_user,'reslist':reslist,'pagination':pagination_res,'error_msg':error_msg,'success_msg':success_msg,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		reslist = []
		active_user = get_user_grp(request.user)
		groupObj = JuiceGroupnames.objects.all().order_by('name')
		page = int(self.request.GET.get('page') or 1)
		limit =int(self.request.GET.get('limit') or 20)
		pagination_res = pagination(groupObj,limit,page)
		for customer in pagination_res:
			res_dict =  {}
			res_dict['customergrp_id'] = customer.groupnameid
			res_dict['customername']  = customer.name
			vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
			hostidlist = []
			for vm in vmgroupobj:
				hostidlist.append(vm.vm)
			#ovm_vmlist, infini_serverlist ,par3_serverlist= get_servernames('',hostidlist)
			res_dict['vmlist'] =set(hostidlist)# ovm_vmlist+infini_serverlist+par3_serverlist)
			reslist.append(res_dict)
		return render(request,'webapp/customer_grplist.html',{'active_user':active_user,'reslist':reslist,'pagination':pagination_res,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

			
# ----- Provision to create a new Customer Group or edit aan existing one -----# 
class CustomerGroup(View):
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		groupid = int(self.request.GET.get('groupid') or 0)
		group_name = ''
		group_acronym = ''
		group_vmlist =self.request.GET.getlist('vmlist')  or []
		vmlist = []
		error_msg = ''
		try:
			ovm_vmlist = []
			infini_vmlist = []
			ovm_vmlist = get_ovm_serverlist()
			infini_vmlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmware_serverlist = get_vmware_serverlist()
			vmlist =set( ovm_vmlist+infini_vmlist+par3_serverlist+vmware_serverlist)
			if groupid:
				groupobj = JuiceGroupnames.objects.filter(groupnameid = groupid)
				for elem in groupobj:
					group_name = elem.name
					group_acronym = elem.acronym
					groupvmobj = JuiceGroupvm.objects.filter(groupid=groupid)
					for vm in groupvmobj:
						group_vmlist.append(vm.vm)
		except Exception as e:
			print ("Customer Group Creation form error - ", e)
			error_msg = "Exception handled in Customer group creation form"
		return render(request,'webapp/customer_grp.html',{'active_user':active_user,'error_msg':error_msg,'group_acronym':group_acronym,'group_name':group_name,'selected_vmlist':group_vmlist,'groupid':groupid,'vmlist':vmlist,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	def post(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		grp_id = int(self.request.POST.get('groupid') or 0)
		customer_grp = self.request.POST.get('customer_grp')or 'Anonymous'
		selected_vms = self.request.POST.getlist('vmlist') or []
		acronym = self.request.POST.get('acronym') or customer_grp[:4]
		try:
			grp_obj = JuiceGroupnames.objects.filter(name=customer_grp) if grp_id == 0 else JuiceGroupnames.objects.filter(groupnameid = grp_id)
			if len(grp_obj) == 0:
				obj = JuiceGroupnames.objects.create(name=customer_grp,acronym = acronym)
				grpid = obj.groupnameid
				for vm_name in selected_vms:
					JuiceGroupvm.objects.create(groupid = grpid,vm=vm_name)
				return redirect('/webapp/customer_grplist?success=1')
			else:
				existingid = 0
				for grp in grp_obj:
					existingid = grp.groupnameid
				obj = JuiceGroupnames.objects.get(groupnameid=existingid)
				obj.name=customer_grp
				obj.acronym = acronym
				obj.save()
				obj2 = JuiceGroupvm.objects.filter(groupid = existingid).delete()
				for vm_name in selected_vms:
					JuiceGroupvm(groupid = existingid,vm=vm_name).save()
				return redirect('/webapp/customer_grplist?update=1')
		except Exception as e:
			error_msg = "Exception handled in Customer group creation form post"
			print ("Customer Group Creation form post error - ",e)
			ovm_vmlist = get_ovm_serverlist()
			infini_vmlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmware_serverlist = get_vmware_serverlist()
			vmlist = set(ovm_vmlist+infini_vmlist+par3_serverlist+vmware_serverlist)
			return render(request,'webapp/customer_grp.html',{'active_user':active_user,'vmlist':vmlist.json(),'back_url':request.META.get('HTTP_REFERER') or '/webapp'})	
