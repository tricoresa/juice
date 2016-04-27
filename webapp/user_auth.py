from django.views.generic.base import View
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.forms import PasswordChangeForm
from webapp.utility import *
from django.contrib  import auth
from django.contrib.auth.models import User,Permission,Group
from django.core.context_processors import csrf
from webapp.user_register import MyRegistrationForm,MyEditForm
#from webapp.models import  AuthUser,AuthGroupPermissions

#--------User registration and Info update form ---- #
class RegisterUser(View):
        def post(self,request,id=None):
                if login_required(request.user):
                        return redirect('/webapp/login?next='+request.path)
                instance = User.objects.using('default').get(id=id) if id  else None
                errorlist=[]
                active_user = get_user_grp(request.user)
                form =MyRegistrationForm(data=request.POST,instance=instance)
                if instance:
                        form = MyEditForm(data=request.POST,instance = instance)
                if form.is_valid():
                        form.save()
                        return redirect('/webapp/userlist?success=1')
                else:
                        errorlist.append( form.errors)
                        url = '/webapp/register' if id == None else '/webapp/register/'+str(id)
                        return render(request,'webapp/register.html',{'error':errorlist,'url':url,'back_url':request.META.get('HTTP_REFERER') or '/webapp','active_user':active_user})
        def get(self,request,id=None):
                if login_required(request.user):
                        return redirect('/webapp/login?next='+request.path)
                usergrp = get_user_grp(request.user) 
                instance = User.objects.get(id=id) if id else None
                if usergrp in (0,1) or instance == request.user:
                        args = {}
                        args.update(csrf(request))
                        args['form'] = MyRegistrationForm(instance=instance)
                        if instance:
                                args['form'] = MyEditForm(instance = instance)
                        args['id']=id
                        args['back_url']=request.META.get('HTTP_REFERER') or '/webapp'
                        args['active_user'] = usergrp
                        return render(request,'webapp/register.html', args)
                else:
                        return render(request,'webapp/register.html',{"error":"Sorry! You are not admin privileged!",'back_url':request.META.get('HTTP_REFERER') or '/webapp','active_user':usergrp})

#----- Registered User list with EDIT/DELETE functioanlity on the list ----- #
class UserList(View):
        def get (self,request):
                if login_required(request.user):
                        return redirect('/webapp/login?next='+request.path)
                active_user = get_user_grp(request.user)
                group_id = request.user.groups.values_list('id',flat=True)
                if len(group_id)>0:
                        group_id = group_id[0]
                userobj = User.objects.using('default').all().order_by('username')
                selected_dir =int(request.COOKIES.get('director') or 0)
                success = int(self.request.GET.get('success',0))
                limit = int(self.request.GET.get('limit') or 25)
                page = int(self.request.GET.get('page') or 1)
                errorlist = self.request.GET.get('error')
                pagination_res = pagination(userobj,limit,page)
                userlist= []
                for user in pagination_res:
                        user_dict ={}
                        user_dict['username']= user.username
                        user_dict['first_name']=user.first_name
                        user_dict['last_name']=user.last_name
                        user_dict['email']=user.email
                        user_dict['id']=user.id
                        user_dict['superuser'] = 1 if user.is_superuser else 0
                        user_dict['grouplist'] = []
                        grplist = user.groups.all()#.values_list('id',flat=True)
                        for grp in grplist:
                                grp = Group.objects.using('default').get(id=grp.id)
                                user_dict['grouplist'].append(grp.name)
                        userlist.append(user_dict)

                return render(request,'webapp/userlist.html',{'success':success,'error':errorlist,'userlist':userlist,'pagination':pagination_res,'active_user':active_user,'selected_dir':selected_dir,'back_url':request.META.get('HTTP_REFERER') or '/webapp'})
class Login(View):
        def get(self,request):
                next = request.GET.get('next','/webapp')
                error = request.GET.get('error') or ''
                if request.user.is_authenticated():
                        return redirect(next)
                else:
                        return render(request,'webapp/login.html',{'next':next,'error':error})
        def post(self,request):
                username = request.POST.get('username','')
                password = request.POST.get('password','')
                #next = request.POST.get('next','/webapp') or request.META.get('HTTP_REFERER')
                #if next == "":
                next =  '/webapp'
                user  =auth.authenticate(username=username,password=password)
                if user is not None:
                        auth.login(request,user) 
                        request.session['user'] = user.id
                        request.session.set_expiry(86400)
                        return redirect(next)
                else:
                        return render(request,'webapp/login.html',{'next':next,'error':'Your login credentials are invalid. Try Again!'})
def logout(request):
        auth.logout(request)
        error = request.GET.get('error') or ''
        return render(request,'webapp/login.html',{'next':'/webapp','error':error})

# ------- Form to facilitate User password editing ---- #
class PasswordEdit(View):
        def post(self,request):
                active_user = get_user_grp(request.user)
                userid = int(request.POST.get('userid') or 0)
                direct = int(request.POST.get('direct') or 0)
                update = int(request.POST.get('update') or 0)
                instance = User.objects.get(id=userid) 
                if instance:
                    if update == 1:
                        errorlist = []
                        form  = PasswordChangeForm(user = instance,data=request.POST)
                        if form.is_valid():
                            form.save()
                            if instance == request.user:
                                return redirect('/webapp/logout')
                            return redirect('/webapp/userlist?success=1')
                        else:
                            errorlist.append( form.errors)
                            url = '/webapp/password/'  
                            return render(request,'webapp/password.html',{'active_user':active_user,'error':errorlist,'back_url':url,'id':userid,'update':1,'direct':direct})

                    else:
                        args = {}
                        args.update(csrf(request))
                        args['form'] = PasswordChangeForm(user = instance)
                        args['id']=userid
                        args['direct'] = direct
                        args['update'] = update
                        args['back_url'] = "/webapp/register/"+str(userid) if direct == 0 else '/webapp'
                        args['active_user'] = active_user
                        return render(request,'webapp/password.html',args)
                else:
                        errorlist = ['Not Authorized for this action']
                        return render(request,'webapp/userlist.html',{'error':errorlist})

class DeleteUser(View):
        def post(self,request):
                errorlist = []
                idlist=self.request.POST.getlist('check[]')
                for id in idlist:
                        try:
                                User.objects.get(pk=id).delete()
                        except:
                                errorlist.append(id)
                if len(errorlist) == 0:
                        return redirect('/webapp/userlist?success=1')
                else:
                        return redirect('/webapp/userlist?error='+str(errorlist))
