# File contains all the REST API
from django.views.generic.base import View
from webapp.models import *
from webapp.views import get_result_usage
import json,time
from django.http import HttpResponse


                # -------------------------------------------------#
	        #  Module to get the VM/Disk details for the specified customer group in REST API
                # -------------------------------------------------#
class diskDetails(View):
	def get(self,request):
		cust_grp = str(self.request.GET.get('customergroup')).split(',')
		server = str(self.request.GET.get('server')).split(',') 
		res_dict,host_count,vm_count,allocated,error  = get_result_usage(cust_grp,server)
		return HttpResponse(json.dumps(res_dict))

class diskAllocated(View):
	def get(self,request):
		res_list = []
		server = str(self.request.GET.get('server')).split(',')
		server_result,host_count,vm_count,allocated,error  = get_result_usage([],server)
		if len(server) == 1:
			res_dict = {}
			res_dict['server'] = server[0]
			res_dict['total_size'] = allocated
			res_list.append(res_dict)
		else:
			for res in server_result:
				res_dict = {}
				res_dict['server'] = res
				res_dict['total_size']=server_result[res]['total_size']
				res_list.append(res_dict)
		return HttpResponse(json.dumps(res_list))


