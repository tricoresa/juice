from django.conf.urls import patterns, url,include
from webapp import views,user_auth
urlpatterns = patterns('',
    url(r'^$',views.Summary.as_view()),
    url(r'^unmapped_disk/$',views.UnmappedDisk.as_view()),
    url(r'^csvexport/$',views.CSVExport.as_view()),
    url(r'^login/',user_auth.Login.as_view()),
    url(r'^logout/',user_auth.logout),
    url(r'^register/(?P<id>\d+)/$',user_auth.RegisterUser.as_view()),
    url(r'^userlist/',user_auth.UserList.as_view()),
    url(r'^register/$',user_auth.RegisterUser.as_view()),
    url(r'^delete/',user_auth.DeleteUser.as_view()),
    url(r'^password/',user_auth.PasswordEdit.as_view()),
    url(r'^vmreport/$',views.Dashboard.as_view()),
    url(r'^repositoryreport/$',views.Repository.as_view()),
    url(r'^customergroup/',views.CustomerGroup.as_view()),
    url(r'^customer_grplist/',views.CustomerGroupList.as_view()),
)
