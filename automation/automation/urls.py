from django.contrib import admin
from django.conf.urls import *
from hotel.views import *


urlpatterns = [
  url(r'^$', main_page),
  url(r'^login/$', login_page),
   url(r'^stafflogin/$', staff_login_page),
  url(r'^logout/$', logout_view),
  url(r'^room/$', room_view),
  url(r'^active_resr/$', active_resr),
  url(r'^reservation_change/$', reservation_change),
  url(r'^(?P<roomNo>.+)/room_status/$', room_status),
  url(r'^(?P<res_id>.+)/res_del/$', res_del),
  url(r'^(?P<res_id>.+)/res_view/$', res_view),
  url(r'^(?P<res_id>.+)/res_edit/$', res_edit),
  url(r'^(?P<res_id>.+)/res_ack/$', res_ack),
  # url(r'^ack/$', ack),
  url(r'^signup/$', signup_view),
  url(r'^(?P<username>[A-Z{20}]+)/usrhome/$', usrhome),
  url(r'^(?P<username>[A-Z{20}]+)/reservation_form/$', reservation_form),
  url(r'^(?P<username>[A-Z{20}]+)/reservation_ack/$', reservation_ack),
  url(r'^(?P<username>[A-Z{20}]+)/reservation_view/$', reservation_view),
  url(r'^(?P<username>[A-Z{20}]+)/reservation_management/$', reservation_management),
  url(r'^(?P<username>[A-Z{20}]+)/reservation_decide/$', reservation_decide),
  # url(r'^forgotpass/$', forgot_password),
  url(r'^admin/', include(admin.site.urls)),
  ]
