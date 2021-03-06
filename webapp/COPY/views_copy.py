from django.shortcuts import render
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from webapp.models import JuiceGroupnames,JuiceGroupvm
import json,csv
from django.utils.encoding import smart_str
from webapp.utility import *
from webapp.infinibox import *
from django.views.generic.base import View
from django.shortcuts import render,get_object_or_404,redirect

# ***************************************************
#Intro - Vmreport allows the user to have a detailed view of all the VM/Server(from OVM/Infinibox)
#which are registered in a customer group, based on the available filters on the VMreport."""
# ***************************************************

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
		selected_grpid = int(self.request.GET.get('group') or 0)
		if selected_grpid > 0:
			groupObj = JuiceGroupnames.objects.filter(groupnameid=selected_grpid).order_by('name')
		else:
			groupObj = JuiceGroupnames.objects.all().order_by('name')
		page = int(self.request.GET.get('page') or 1)
		limit =int(self.request.GET.get('limit') or 10)
		pagination_res = pagination(groupObj,limit,page)
		infiniserverlist = get_serverlist()
		infini_vmid_list = [vm.get('value') for vm in infiniserverlist]
		try:
			for customer in pagination_res:
				res_dict =  {}
				res_dict['physical_disk_size'] = 0
				res_dict['virtual_disk_size'] = 0
				total_grp_usage = 0
				res_dict['groupname']  = customer.name
				res_dict['groupid'] = customer.groupnameid
				ovm_juiceVMObject = JuiceGroupvm.objects.filter(groupid=customer.groupnameid).exclude(vm__in = infini_vmid_list)
				infini_juiceVMObject = JuiceGroupvm.objects.filter(groupid=customer.groupnameid,vm__in = infini_vmid_list) 
				if ovm_juiceVMObject:
					res_dict['source'] = 1
					reslist,total_grp_usage = calculate_size(ovm_juiceVMObject.values_list('vm',flat=True))
					for elem in reslist:
						if len(elem.get('virtualist')) > 0 :
							for vm_json in elem['virtualist']:
								res_dict['virtual_disk_size'] += vm_json['total']
						if len(elem.get('physicalist')) > 0:
							for vm_json in elem['physicalist']:
								res_dict['physical_disk_size'] += vm_json['total']
					res_dict['size'] = res_dict['physical_disk_size']+res_dict['virtual_disk_size']
				if infini_juiceVMObject:
					res_dict['source'] = 2
					vmlist = infini_juiceVMObject.values_list('vm',flat=True)
					res_list,total_grp_usage = infini(set(vmlist),limit)
					res_dict['size'] = 0
					for res in res_list:
						for elem in res.get('disk_list'):
							res_dict['size'] += elem['size']
				grp_list.append(res_dict)
		except Exception as e:
			print ("Summary Module error - ",e)
			error_msg = "Exception handled in Summary module"

		return render(request,'webapp/summary.html',{'active_user':active_user,'error_msg':error_msg,'grp_list':grp_list,'customergrouplist':customergrouplist,'selected_grpid':selected_grpid,'pagination':pagination_res,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

class CSVExport(View):
	def post(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		ajax = int(self.request.POST.get('ajax') or 0)
		reslist = json.loads(self.request.POST.get('reslist'))
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=VMReport.csv'
		writer = csv.writer(response, csv.excel)
		response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
		writer.writerow([
			smart_str('Type'),
			smart_str('VM Name'),
			smart_str('Server Name'),
			smart_str('Repo Name'),
			smart_str('Disk Id'),
			smart_str('Disk Name'),
			smart_str('Disk Size'),
		])
		result = []
		for res in reslist:
			if res.get('virtualist') or res.get('physicalist'):
				tmp_list = res.get('virtualist') or res.get('physicalist')
				for disk in tmp_list:
					res_dict = {}
					res_dict ['type'] = 'OVM'
					res_dict['repo'] = disk.get('repo_name')
					res_dict['diskid'] = disk.get('id')
					res_dict['diskname'] = disk.get('name')
					res_dict['disksize'] = disk.get('size')
					res_dict['vm'] = res.get('vmname')
					res_dict['servername'] = res.get('servername')
					result.append(res_dict)
			else:
				for disk in res['disk_list']:
					res_dict = {}
					res_dict['type'] = "Infinibox"
					res_dict['repo'] = ''
					res_dict['diskid'] = disk.get('id')
					res_dict['diskname'] = disk.get('name')
					res_dict['disksize'] = disk.get('size')
					res_dict['vm'] = ''
					res_dict['servername'] =  res.get('servername')
					result.append(res_dict)
		for obj in result:
			writer.writerow([
				smart_str(obj['type']),
				smart_str(obj['vm']),
				smart_str(obj['servername']),
				smart_str(obj['repo']),
				smart_str(obj['diskid']),
				smart_str(obj['diskname']),
				smart_str(obj['disksize']),
			])
		return response
		
#----Dashboard is th VM report where Vm from OVM and disks from INfinibox are listed with respective repo name, disk name ,disk size
class Dashboard(View):
	def get(self,request):
		if request.method == 'GET':
			if login_required(request.user):
				return redirect('/webapp/login?next='+request.path)
			active_user = get_user_grp(request.user)
			ajax = int(self.request.GET.get('ajax') or 0)
			pagination_res = None
			serverlist = []
			reslist = []
			total_usage = 0
			error_msg = ''
			selected_groupname = ''
			limit =int(self.request.GET.get('limit') or 0)
			selected_limit = limit
			source = int(self.request.GET.get('source') or 0)
			custgrp = int(self.request.GET.get('group') or 0)

			# ---------------List of all VM in OVM, irrespective of those present in customer groups
			all_vmidlist = []	
			for vm in vmdata:
				all_vmidlist.append(vm['id']['value'])
	
			# -----------------
			if custgrp > 0:
				selected_groupname = JuiceGroupnames.objects.get(groupnameid=custgrp).name
			server = self.request.GET.get('server') or ''
			customergrouplist = JuiceGroupnames.objects.all()
			ovmserverlist = []
			for s in serverdata:
				ovmserverlist.append(s['id'])

			infiniserverlist = get_serverlist()
			infini_vmid_list = [vm.get('value') for vm in infiniserverlist]
			infini_groupid_list = JuiceGroupvm.objects.filter(vm__in = infini_vmid_list).values_list('groupid',flat=True)
			infini_customergrouplist  = customergrouplist.filter(groupnameid__in = infini_groupid_list)
			ovm_groupid_list = JuiceGroupvm.objects.all().exclude(vm__in = infini_vmid_list ) .values_list('groupid',flat=True)
			ovm_customergrouplist = customergrouplist.filter(groupnameid__in = ovm_groupid_list)
			try:
				#----- Handling AjAX request on filter selection -----#
				if ajax > 0:
					
					if source ==0:
						serverlist =  ovmserverlist+infiniserverlist
					if source ==1:
						serverlist = ovmserverlist
						customergrouplist = ovm_customergrouplist
					if source ==2:
						serverlist = infiniserverlist
						customergrouplist = infini_customergrouplist
					cust_list = []
					for cust in customergrouplist:
						cust_dict = {}
						cust_dict['id']= cust.groupnameid
						cust_dict['name'] = cust.name
						cust_list.append(cust_dict)
					return HttpResponse(json.dumps({'serverlist':serverlist,'customergrouplist':cust_list}))
				#-------------------------------------------#
				if source == 1:
					# -------- All VM from OVM ------------- #
					serverlist = ovmserverlist
					customergrouplist = ovm_customergrouplist
					ovm_obj = None #JuiceGroupvm.objects.all().exclude(vm__in = infini_vmid_list)
					if custgrp != 0 :
						ovm_obj = JuiceGroupvm.objects.filter(groupid = custgrp)
					if server != '' and server != '0':
						vmid_list = []
						for s in serverdata:
							if s['id']['value'] == str(server):
								for vm in s['vmIds']:
									vmid_list.append(vm['value'])
						print (vmid_list)
						ovm_obj = ovm_obj.filter(vm__in = vmid_list) if ovm_obj else JuiceGroupvm.objects.filter(vm__in = vmid_list)
					if limit ==0:
						limit = ovm_obj.count() if ovm_obj and ovm_obj.count() >0  else len(all_vmidlist)
					if ovm_obj != None:
						
						reslist,total_usage = calculate_size(ovm_obj.values_list('vm',flat=True)[:limit])
					else:
						reslist,total_usage = calculate_size(all_vmidlist[:limit])	
					print (len(reslist))
				if source == 2:
					# ---------- All server from infinibox -------  #
					infinilist = []    	
					customergrouplist = infini_customergrouplist
					infini_obj = None #JuiceGroupvm.objects.all().filter(vm__in = infini_vmid_list)
					serverlist = infiniserverlist
					if custgrp != 0:
						infini_obj =  JuiceGroupvm.objects.filter(groupid = custgrp)
					if server != '' and server != '0' and server.isdigit():
						infini_obj = infini_obj.filter(vm=server) if infini_obj else JuiceGroupvm.objects.filter(vm=server)
					if infini_obj != None:
						infinilist = set( infini_obj.values_list('vm',flat=True))
						if len(infinilist) == 0:
							infinilist = None
					reslist,total_usage = infini(infinilist,limit)
					print (len(reslist))
				if source == 0:    	
					#--------- All VM/server from OVM/infinibox ----------- #
					ovmreslist = []
					ovmtotal_usage = 0
					infinireslist = []
					infinitotal_usage = 0
					limit = 0
					serverlist = ovmserverlist + infiniserverlist
					ovm_obj = None
					infini_obj = None #JuiceGroupvm.objects.all().filter(vm__in = infini_vmid_list)
					infinilist = []
					if custgrp != 0:
						ovm_obj = JuiceGroupvm.objects.filter(groupid = custgrp).exclude(vm__in = infini_vmid_list)
						infini_obj = JuiceGroupvm.objects.filter(vm__in = infini_vmid_list,groupid = custgrp)
					if server != '0' and server != '' :
						if server.isdigit():
							if ovm_obj != None and len(ovm_obj) > 0:
								ovm_obj = ovm_obj.filter(vm=server)
							else:
								infini_obj = infini_obj.filter(vm=server) if infini_obj else JuiceGroupvm.objects.filter(vm=server) 
						else:
							vmid_list = []
							for s in serverdata:
								if s['id']['value'] == str(server):
									for vm in s['vmIds']:
                                                                        	vmid_list.append(vm['value'])
							if infini_obj != None  and len(infini_obj) >0 :
								infini_obj = infini_obj.filter(vm__in = vmid_list)
							else:
								ovm_obj = ovm_obj.filter(vm__in = vmid_list) if ovm_obj else JuiceGroupvm.objects.filter(vm__in = vmid_list)

		 
					if infini_obj != None:
						if len(infini_obj)> 0:
							infinilist = set(infini_obj.values_list('vm',flat=True))
						else:
							infinilist = None
					if ovm_obj != None and len(ovm_obj)>0:
						infinilist = None
						ovmreslist,ovmtotal_usage = calculate_size(ovm_obj.values_list('vm',flat=True))
					elif custgrp == 0 and (server == '0' or server == ''):
						ovmreslist,ovmtotal_usage = calculate_size(all_vmidlist)	
					infinireslist,infinitotal_usage = infini(infinilist,limit)
					print (len(infinireslist))
					print (len(ovmreslist))
					reslist = infinireslist+ovmreslist
					total_usage = infinitotal_usage + ovmtotal_usage
			except Exception as e:
				print ("Dashboard Module error - ",e)
				error_msg = "Exception handled in Dashboard Module"
		return render(request,'webapp/dashboard.html',{'active_user':active_user,'error_msg':error_msg,'limit':selected_limit,'source':source,'pagination':pagination_res,'selected_server':server,'serverlist':serverlist,'reslist':reslist,'selected_groupid':custgrp,'customergrouplist':customergrouplist,'infini_serverlist':infiniserverlist,'ovm_serverlist':ovmserverlist,'infini_custgrplist':infini_customergrouplist,'ovm_custgrplist':ovm_customergrouplist,'selected_grpname':selected_groupname,'total_usage':total_usage,'exclude_list':exclude_list,'back_url':request.META.get('HTTP_REFERER') or '/webapp','ovm_customergrouplist':ovm_customergrouplist,'infini_customergrouplist':infini_customergrouplist})		
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
		limit =int(self.request.POST.get('limit') or 10)
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
				res_dict['vmlist'] = []
				vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
				for vm in vmgroupobj:
					if not vm.vm.isdigit():
						for v in vmdata:
							if vm.vm == v['id']['value']:
								res_dict['vmlist'].append(v['id']['name'])
					else:
						infini_server = get_serverlist('all',int(vm.vm))
						res_dict['vmlist'].append(infini_server[0]['name'])
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
		limit =int(self.request.GET.get('limit') or 10)
		pagination_res = pagination(groupObj,limit,page)
		for customer in pagination_res:
			res_dict =  {}
			res_dict['customergrp_id'] = customer.groupnameid
			res_dict['customername']  = customer.name
			res_dict['vmlist'] = []
			vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
			for vm in vmgroupobj:
				if not vm.vm.isdigit():
					for v in vmdata:
						if vm.vm == v['id']['value']:
							res_dict['vmlist'].append(v['id']['name'])

				else:
					infini_server = get_serverlist('all',int(vm.vm))
					res_dict['vmlist'].append(infini_server[0]['name'])
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
		group_vmlist = []
		vmlist = []
		error_msg = ''
		try:
			ovm_vmlist = []
			infini_vmlist = []
			for vm in vmdata:
				ovm_vmlist.append(vm['id'])
			infini_vmlist = get_serverlist()
			vmlist = ovm_vmlist+infini_vmlist
			if groupid:
				groupobj = JuiceGroupnames.objects.filter(groupnameid = groupid)
				for elem in groupobj:
					group_name = elem.name
					groupvmobj = JuiceGroupvm.objects.filter(groupid=groupid)
					for vm in groupvmobj:
						group_vmlist.append(vm.vm)
		except Exception as e:
			print ("Customer Group Creation form error - ", e)
			error_msg = "Exception handled in Customer group creation form"
		return render(request,'webapp/customer_grp.html',{'active_user':active_user,'error_msg':error_msg,'group_name':group_name,'selected_vmlist':group_vmlist,'groupid':groupid,'vmlist':vmlist,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	def post(self,request):
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		grp_id = int(self.request.POST.get('groupid') or 0)
		customer_grp = self.request.POST.get('customer_grp')or 'Anonymous'
		selected_vms = self.request.POST.getlist('vmlist') or []
		try:
			grp_obj = JuiceGroupnames.objects.filter(name=customer_grp) if grp_id == 0 else JuiceGroupnames.objects.filter(groupnameid = grp_id)
			if len(grp_obj) == 0:
				obj = JuiceGroupnames.objects.create(name=customer_grp)
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
				obj.save()
				obj2 = JuiceGroupvm.objects.filter(groupid = existingid).delete()
				for vm_name in selected_vms:
					JuiceGroupvm(groupid = existingid,vm=vm_name).save()
				return redirect('/webapp/customer_grplist?update=1')
		except Exception as e:
			error_msg = "Exception handled in Customer group creation form post"
			print ("Customer Group Creation form post error - ",e)
			for vm in vmdata:
				vmlist.append(vm['id'])
			return render(request,'webapp/customer_grp.html',{'active_user':active_user,'vmlist':vmlist.json(),'back_url':request.META.get('HTTP_REFERER') or '/webapp'})	
