from django.db import models

# Create your models here.
class JuiceGroupnames(models.Model):
	groupnameid = models.AutoField(primary_key=True)
	name = models.TextField()
	acronym = models.TextField()
	class Meta:
		managed = False
		db_table = 'juice_groupnames'

class JuiceGroupvm(models.Model):
	groupvmid = models.AutoField(primary_key=True)
	vm = models.TextField()
	groupid = models.IntegerField()
	class Meta:
		managed = False
		db_table = 'juice_groupvm'

	def apply_filter(self,**kwargs):
		vmObj = JuiceGroupvm.objects.all()
		if 'groupid' in kwargs and kwargs['groupid'] > 0:
			vmObj = vmObj.filter(groupid = kwargs['groupid'])
		if 'vmlist' in kwargs and len(kwargs['vmlist']) >0 :
			vmObj = vmObj.filter(vm__in = kwargs['vmlist'])
		if 'serverlist' in kwargs and len(kwargs['serverlist']) >0 :
                        vmObj = vmObj.filter(vm__in = kwargs['serverlist'])
		return vmObj
	

