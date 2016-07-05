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
		print (cust_grp)
		res_dict,host_count,usage,error  = get_result_usage(cust_grp)
		return HttpResponse(json.dumps(res_dict))
