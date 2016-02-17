from django.shortcuts import render
from django.http import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from webapp.models import JuiceGroupnames,JuiceGroupvm
import json,csv
from django.utils.encoding import smart_str
from webapp.utility import *
from webapp.infinibox import *
from webapp.par3 import *
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
		
		try:
			for customer in pagination_res:
				res_dict =  {}
				res_dict['physical_disk_size'] = 0
				res_dict['virtual_disk_size'] = 0
				res_dict ['size'] = 0  
				total_grp_usage = 0
				res_dict['groupname']  = customer.name
				res_dict['groupid'] = customer.groupnameid
				acronym = customer.acronym
				vlist,hostlist = applyfilter(acronym)
				if len(vlist) >  0:
					ovm_res,total_grp_usage = get_ovm(vlist)
					for elem in ovm_res:
						if len(elem.get('virtualist')) > 0 :
							for vm_json in elem['virtualist']:
								res_dict['virtual_disk_size'] += vm_json['total']
						if len(elem.get('physicalist')) > 0:
							for vm_json in elem['physicalist']:
								res_dict['physical_disk_size'] += vm_json['total']
					res_dict['size'] = res_dict['physical_disk_size']+res_dict['virtual_disk_size']	                
				if len(hostlist)>0 :
					infini_res,total_grp_usage = get_infini(hostlist,limit)
					for res in infini_res:
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
		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)	
		source = int(self.request.GET.get('source') or 0)
		server = self.request.GET.getlist('server') or []
		custgrp = int(self.request.GET.get('group') or 0)
		limit = 0
		cust_grplist = JuiceGroupnames.objects.all().order_by('name')
		ovm_serverlist = get_ovm_serverlist()
		infini_serverlist = get_infini_serverlist()
		par3_serverlist = get_3par_serverlist()
		serverlist= ovm_serverlist+infini_serverlist +par3_serverlist
		newserverlist = sorted(serverlist, key=lambda k: k['name'])
		cust_acronym = ''
		"""if custgrp > 0:
			cust_acronym = JuiceGroupnames.objects.get(groupnameid = custgrp).acronym
		vlist , hostlist = applyfilter(cust_acronym,server)
		#par3_result,par3_usage = get_3par()
		if len(vlist)>0:
			ovmresult,ovm_usage  = get_ovm(vlist)
		elif  cust_acronym == "" and len(server) == 0:
			ovmresult,ovm_usage = get_ovm([])
		else:
			ovmresult,ovm_usage = [],0
		if len(hostlist)>0:
			infiniresult,infini_usage = get_infini(hostlist,limit)
		elif cust_acronym == "" and len(server) == 0:
			infiniresult,infini_usage = get_infini([],limit)
		else:
			infiniresult,infini_usage = [],0
		result = ovmresult + infiniresult # + par3_result
		total_usage = ovm_usage+infini_usage # + par3_usage"""
		result = []
		total_usage  = 0
		return render(request,'webapp/dashboard.html',{'reslist':result,'active_user':active_user,'source':source,'server':server,'serverlist':newserverlist,'cust_grp':custgrp,'customergrouplist':cust_grplist,'total_usage':total_usage,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})	
	def post(self,request):

		if login_required(request.user):
			return redirect('/webapp/login?next='+request.path)
		active_user = get_user_grp(request.user)
		source = int(self.request.POST.get('source') or 0)
		custgrp = int(self.request.POST.get('group') or 0)
		server = self.request.POST.getlist('server') or []
		limit = 0#int(self.request.POST.get('limit') or 0)
		cust_grplist = JuiceGroupnames.objects.all().order_by('name')
		if custgrp > 0:
			cust_acronym = JuiceGroupnames.objects.get(groupnameid = custgrp).acronym 
		else:
			cust_acronym = ''
		ovm_serverlist = get_ovm_serverlist()
		infini_serverlist = get_infini_serverlist()
		par3_serverlist = get_3par_serverlist()
		serverlist= ovm_serverlist+infini_serverlist+par3_serverlist
		newserverlist = sorted(serverlist, key=lambda k: k['name'])
	
		if source == 0:
			result= ovmresult+infiniresult
			total_usage = ovm_usage+infini_usage
		if source ==1:
			vlist  = applyfilter(cust_acronym,server,source=1)
			if len(vlist)>0:
				ovmresult,ovm_usage  = get_ovm(vlist)
			elif  cust_acronym == "" and len(server) == 0:
				ovmresult,ovm_usage = get_ovm([])
			else:
				ovmresult,ovm_usage = [],0
			result = ovmresult
			total_usage = ovm_usage
		if source ==2:
			hostlist  = applyfilter(cust_acronym,server,source=2)
			if len(hostlist)>0:
				infiniresult,infini_usage = get_infini(hostlist,limit)
			elif cust_acronym == "" and len(server) == 0:
				infiniresult,infini_usage = get_infini([],limit)
			else:
				infiniresult,infini_usage = [],0

			result  = infiniresult
			total_usage = infini_usage
		if source == 3:
			par3_hostlist  = applyfilter(cust_acronym,server,source=3)
			if len(par3_hostlist)>0:
				par3_result,par3_usage = get_3par(par3_hostlist)
			elif cust_acronym == "" and len(server) == 0:
				par3_result,par3_usage = get_3par([])
			else:
				par3_result,par3_usage = [],0

			result = par3_result
			total_usage = par3_usage	
		return render(request,'webapp/dashboard.html',{'reslist':result,'active_user':active_user,'limit':limit,'source':source,'server':server,'serverlist':newserverlist,'cust_grp':custgrp,'customergrouplist':cust_grplist,'total_usage':total_usage,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})

	
	
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
				ovm_vmlist, infini_serverlist,par3_serverlist = get_servernames(customer.acronym)
				res_dict['vmlist'] = ovm_vmlist+infini_serverlist+par3_serverlist
				"""vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
				for vm in vmgroupobj:
					if not vm.vm.isdigit():
						for v in vmdata:
							if vm.vm == v['id']['value']:
								res_dict['vmlist'].append(v['id']['name'])
					else:
						infini_server = get_infini_serverlist()
						res_dict['vmlist'].append(infini_server[0]['name'])"""
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
			ovm_vmlist, infini_serverlist ,par3_serverlist= get_servernames(customer.acronym)

			res_dict['vmlist'] = ovm_vmlist+infini_serverlist+par3_serverlist
			"""vmgroupobj = JuiceGroupvm.objects.filter(groupid = customer.groupnameid)
			for vm in vmgroupobj:
				if not vm.vm.isdigit():
					for v in vmdata:
						if vm.vm == v['id']['value']:
							res_dict['vmlist'].append(v['id']['name'])

				else:
					infini_server = get_infini_serverlist()
					res_dict['vmlist'].append(infini_server[0]['name'])"""
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
		group_vmlist =self.request.GET.get('vmlist')  or ''
		group_vmlist = group_vmlist.split(",")
		vmlist = []
		error_msg = ''
		try:
			ovm_vmlist = []
			infini_vmlist = []
			for vm in vmdata:
				ovm_vmlist.append(vm['id'])
			infini_vmlist = get_infini_serverlist()
			par3_serverlist = get_3par_serverlist()
			vmlist = ovm_vmlist+infini_vmlist+par3_serverlist
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
			for vm in vmdata:
				vmlist.append(vm['id'])
			return render(request,'webapp/customer_grp.html',{'active_user':active_user,'vmlist':vmlist.json(),'back_url':request.META.get('HTTP_REFERER') or '/webapp'})	
