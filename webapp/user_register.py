from django import forms
from django.contrib.auth.models import User,Permission,Group
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.contenttypes.models import ContentType
class MyRegistrationForm(UserCreationForm):
        #email = forms.EmailField(required = True)
        #password1 = forms.CharField(widget=forms.PasswordInput, required=True)
        #password2 = forms.CharField(widget=forms.PasswordInput, required=True)
        class Meta:
                model = User
                exclude = ('user_permissions','password','is_staff','password1','password2')
        def clean_username(self):
                instance = getattr(self, 'instance', None)
                if instance and instance.pk:
                    return instance.username
                else:
                    return self.cleaned_data['username']
        """def clean_password2(self):
                password1 = self.cleaned_data.get("password1", "")
                password2 = self.cleaned_data["password2"]
                if password1 != password2:
                    raise forms.ValidationError(_("The two password fields didn't match."))
                return password2        """
        def save(self,commit=True):
                user = super(UserCreationForm,self).save(commit= False)
                user.set_password(self.cleaned_data["password1"])
                user.email=self.cleaned_data['email']
                user.password1 = self.cleaned_data['password2']
                user.password2 = self.cleaned_data['password2']
                if commit:
                        user.save()
                        user.groups = self.cleaned_data['groups']
                        """for group in self.cleaned_data['groups']:
                        user.groups.add(group)"""
                return user
class MyEditForm(forms.ModelForm):
        class Meta:
                model = User
                exclude = ('password','user_permissions','last_login','date_joined','is_staff','password1','password2')
        def clean_email(self):
                username = self.cleaned_data.get('username')
                email =  self.cleaned_data['email']
                instance = getattr(self, 'instance', None)
                if instance and instance.pk:
                    return  instance.email
                else:
                    return self.cleaned_data['email']

                #if email and User.objects.using('default').filter(email=email).exclude(username=username).count():
                #    raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
                #return email


