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
        host_count = 0
        print ('length of host list = ', len(hostlist))
        if len(hostlist)>0:
            result1,infini_allocated,infini_error = get_infini(hostlist)
            result2,ovm_allocated,ovm_error = get_ovm(hostlist)
            result3,vmware_allocated,vmware_error = get_vmware(hostlist)
            result4,par3_allocated,par3_error = get_3par(hostlist)
            print (len(result1),len(result2),len(result3),len(result4))
            result = result1+result2+result3+result4
            #result.append(ovm_result)
            #result.append(infini_result)
            #result.append(par3_result)
            #result.append(vmware_result)
            print ('result length = ',len(result))
            res_dict = {}
            for res in result:
                for key,value in res.items():
                    if key not in res_dict:
                        res_dict[key] = {'disk_list':[],'total_size':0,'vm_name':''}
                    res_dict[key]['disk_list']+= res[key]['disk_list']
                    res_dict[key]['used_size'] = res[key]['used_size']
                    res_dict[key]['total_size'] += res[key]['total_size']
                    res_dict[key]['source'] = res[key]['source']
                    if res[key]['source'] == 'OVM': 
                        res_dict[key]['server'] = res[key]['servername']
                    elif res[key]['source'] == 'VMware':
                        res_dict[key]['server'] = res[key]['vmhost']
                    else:
                        res_dict[key]['server'] = key
                    res_dict[key]['vm_name'] = res[key]['vm_name'] if 'vm_name' in res[key] else ''
            allocated = ovm_allocated+infini_allocated+par3_allocated+vmware_allocated
            host_list = [val['server'].lower() for key,val in res_dict.items()]
            vm_list = [val['vm_name'].lower() for key,val in res_dict.items()]
            vm_count = len(set(vm_list))
            host_count = len(set(host_list))
            """if len(ovm_error) > 0:
                 error.append(ovm_error) 
            if len(infini_error) > 0:
                error.append(infini_error)
            if len(par3_error)>0:
                error.append(par3_error)
            if len(vmware_error)>0:
                error.append(vmware_error)"""
        else:
            res_dict,usage,error = {},0,''
        return res_dict,host_count,vm_count,allocated,error

#----------------- Module supporting Customer group create / Edit , 'Apply' button functionaly-------------#
class AjaxRequest(View):
	def get(self,request):
		groupid = self.request.GET.get('groupid') or 0
		acronymlist = self.request.GET.get('acronym').split(',')or []
		if groupid >0:
			acronym= JuiceGroupnames.objects.get(groupnameid = groupid).acronym
			return HttpResponse(acronym)


		elif acronymlist!= [''] :

			ovm_serverlist = get_ovm_serverlist()
			infini_serverlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmware_serverlist = get_vmware_serverlist()
			serverlist =set( ovm_serverlist+infini_serverlist+par3_serverlist+vmware_serverlist)
			name_convention = ['psmw','psml','psmu','psmv','pchw','pchl','pchu','pchv', 'nsmw','nsml','nsmu','nsmv','nchw','nchl','nchu','nchv','rsmw','rsml','rsmu','rsmv','rchw','rchl','rchu','rchv','tsmw','tsml','tsmu','tsmv','tchw','tchl','tchu','tchv']

			reslist = []
			for s in serverlist:
				if s[:4] in name_convention:
					server = s[4:]
				else:
					server = s
				for acronym in acronymlist:
					if '!' not in acronym :
						if acronym.strip().lower() in server.lower():
							reslist.append(s)
					else:
						if acronym[1:].strip().lower() in server.lower() and s in reslist:
							reslist.remove(s)
			return HttpResponse(json.dumps({'result':reslist}))
			# on form submit, select all the values of select box 3
			# make sure if left right item swapping buttons are working fine.
		else:
			return HttpResponse(json.dumps({'result':[]}))	
# ------ Module for unmapped Disks and VM listing  --------#
class UnmappedDisk(View):	
	def get(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		error_msg = ''
		result = []
		active_user = get_user_grp(request.user)
		result1,error = get_unmapped_ovm()
		result2,error = get_unmapped_infini()
		result3,error = get_unmapped_3par()
		result4,error= get_unmapped_vmware()
		result = result1+result2+result3+result4
		#result.append(ovm_result)
		#result.append(infini_result)
		#result.append(par3_result)
		#result.append(vmware_result)
		res_dict = {}
		totalsize = 0
		for res in result:
			for key,value in res.items():
				if key not in res_dict:
					res_dict[key] = {'disk_list':[],'total_size':0,'vm_name':''}
				res_dict[key]['disk_list']+= res[key]['disk_list']
				res_dict[key]['total_size'] += res[key]['total_size']
				res_dict[key]['source'] = res[key]['source']
				totalsize += res_dict[key]['total_size'] 
		return render(request,'webapp/unmapped.html',{'total_size':totalsize,'active_user':active_user,'error_msg':error,'res_dict':res_dict,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})		

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
					for dct in ovm_res:
						for key, elem in dct.items():
							if len(elem.get('virtualist')) > 0 :
								for vm_json in elem['virtualist']:
									res_dict['virtual_disk_size'] += vm_json['total']
							if len(elem.get('physicalist')) > 0:
								for vm_json in elem['physicalist']:
									res_dict['physical_disk_size'] += vm_json['total']
					# ------------- Processing Infini result
					infini_res,infini_usage,error = get_infini(vlist)
					res_dict['physical_disk_size'] += infini_usage
					"""for key,res in infini_res.items():
						for elem in res.get('disk_list'):
							res_dict['physical_disk_size'] += elem['size']
							res_dict['size'] += elem['size']
					"""
					# ------------ Processing par3 result
					par3_result,par3_usage,error = get_3par(vlist)
					res_dict['physical_disk_size'] += par3_usage
					"""for key,res in par3_result.items():
						for elem in res.get('disk_list'):
							res_dict['physical_disk_size'] += elem['size']
							res_dict['size'] += elem['size']
					"""
					# ---------- Processing vmware result
					vmware_result,vmware_usage,error= get_vmware(vlist)
					res_dict['virtual_disk_size'] += vmware_usage
					"""for key,res in vmware_result.items():
						for elem in res.get('disk_list'):
							res_dict['virtual_disk_size'] += elem['size']"""
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
		host_count = self.request.POST.get('host_count')
		total_allocated = self.request.POST.get('total_allocated')
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=VMReport.csv'
		writer = csv.writer(response, csv.excel)
		response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
		#writer.writerow([
                #        smart_str('Server count = '+host_count ),
                #        smart_str('Total disk allocated = '+total_allocated),

		#])
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
				res_dict['servername'] = val.get('server')#key if val.get('VMware') != 1 else val.get('vmhost')
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
		total_allocated = 0
		error_notify = ''
		empty_notify  = ''
		newserverlist = []
		cust_acronym = []
		res_dict = {}
		host_count = 0
		vm_count = 0
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
				res_dict,host_count,vm_count,allocated,error = get_result_usage(cust_acronym,server,server_acronym)	
			else:
				res_dict,host_count,vm_count,allocated,error = get_result_usage(cust_acronym)
			total_allocated = allocated
			if len(error)  > 0:
				error_notify = str(error)
			if len(res_dict) == 0:
				if custgrp == 0:
					pass
				else:
					empty_notify = "No result matching the filters"
		except Exception as e:
			error_notify = "Error in Report caluclation - "+str(e)
		return render(request,'webapp/dashboard.html',{'vm_count':vm_count,'host_count':host_count,'error_notify':error_notify,'empty_notify':empty_notify,'resdict_csv':res_dict,'exclude_list':exclude_list,'resdict':OrderedDict(sorted(res_dict.items(), key=lambda t: t[0])),'active_user':active_user,'serverlist':newserverlist,'cust_grp':custgrp,'customergrouplist':cust_grplist,'total_allocated':total_allocated,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	
	
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
			with open('webapp/JSON/repo.json') as data_file:
				repodata = json.load(data_file)
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
				acronym = customer.acronym
				hostlist = get_servernames(acronym.split(','))
				res_dict['vmlist'] = hostlist 
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
			acronym = customer.acronym
			hostlist = get_servernames(acronym.split(','))
			res_dict['vmlist'] = hostlist 
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
			ovm_serverlist = get_ovm_serverlist()
			infini_serverlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmware_serverlist = get_vmware_serverlist()
			

			vmlist =set( ovm_serverlist+infini_serverlist+par3_serverlist+vmware_serverlist)
			if groupid:
				groupobj = JuiceGroupnames.objects.filter(groupnameid = groupid)
				for elem in groupobj:
					group_name = elem.name
					group_acronym = elem.acronym
					group_vmlist = get_servernames(elem.acronym.split(','))
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
		#selected_vms = self.request.POST.getlist('vmlist') or []
		ajax = int(self.request.POST.get('ajax')) or 0
		acronym = self.request.POST.get('acronym') or ''
		try:
			grp_obj = JuiceGroupnames.objects.filter(name=customer_grp) if grp_id == 0 else JuiceGroupnames.objects.filter(groupnameid = grp_id)
			if len(grp_obj) == 0:
				obj = JuiceGroupnames.objects.create(name=customer_grp,acronym = acronym)
				grpid = obj.groupnameid
				#for vm_name in selected_vms:
				#	JuiceGroupvm.objects.create(groupid = grpid,vm=vm_name)
				if ajax == 1:
					return HttpResponse('Succesfully created a group with selected Servers/VMs')
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
				#for vm_name in selected_vms:
				#	JuiceGroupvm(groupid = existingid,vm=vm_name).save()
				if ajax == 1:
					return HttpResponse('Succesfully updated the customer group with selected Server/VMs')
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
