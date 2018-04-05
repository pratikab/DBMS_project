from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate,login,logout
from django.db import transaction, IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import *
import os
from random import randint
from hotel.models import *
from datetime import datetime
import copy
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Max
from django.contrib.auth import get_user_model
User = get_user_model()

import time
counter = 0
def get_id():
	global counter
	x = Reservation.objects.all().aggregate(Max('reservation_id'))['reservation_id__max']
	if  x== None:
		counter = 0
	else:
		counter = x
	counter += 1
	return counter


def check_overlap(x,y):
	a = x.expected_arrival_date
	b = x.expected_departure_date
	for i in y:
		c = i.expected_arrival_date
		d = i.expected_departure_date
		if c <= b <= d :
			return True
		if c <= a <= d:
			return True
	return False
def main_page(request):
	project='Hello'
	# return HttpResponse('Hello World!')
	return render(request,'index.html')

def login_page(request):
	username = request.POST.get('username',False)
	password = request.POST.get('password',False)
	error = ""
	response = render(request,'login.html')
	if username != False:
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				current_user = request.user
				return redirect('/'+user.username+'/usrhome/')
		else:
			error = "Wrong Username or Password!"
			response = render(request,'login.html',{'error':error})

	return response


def staff_login_page(request):
	username = request.POST.get('username',False)
	password = request.POST.get('password',False)
	error = ""
	response = render(request,'stafflogin.html')
	if username != False:
		user = authenticate(username=username,password=password)
		if user is not None:
			if not user.isStaff:
				error = "Not staff member"
				print("Unauthorized Login")
				response = render(request,'stafflogin.html',{'error':error})
				return response
			if user.is_active:
				login(request,user)
				current_user = request.user
				return redirect('/'+user.username+'/usrhome/')
		else:
			error = "Wrong Username or Password!"
			response = render(request,'stafflogin.html',{'error':error})

	return response

def signup_view(request):
	name = request.POST.get('name',False)
	username = request.POST.get('username',False)
	password = request.POST.get('password',False)
	email = request.POST.get('email',False)
	phoNo = request.POST.get('phoNo',False)
	error = ""
	if username != False:
		if User.objects.filter(username=username).exists():
			error = "The username has already taken :P"
		else:
			user = User.objects.create_user(username=username,password=password,isStaff=False)
			user.save()
			customer = Customer(username=username,name=name,phoNo=phoNo,email=email)
			customer.save()
			return redirect('/login/')

	return render(request,'signup.html',{'error':error})

def logout_view(request):
	logout(request)
	response = redirect('/')
	response.delete_cookie('hotel_cookie')
	return response
	# return redirect('/')


@login_required(login_url = '/login/')
def usrhome(request,username):
	"""
	This is the view for homepage.
	This is a function based view.
	"""
	page_title = ("Hotel Management System")  # For page title as well as heading
	return render(
		request,
		'usrhome.html',
		{
			'title': page_title,
			'username': request.user.username,
		}
	)

@login_required(login_url = '/login/')
def room_view(request):
	"""
	This is the view for homepage.
	This is a function based view.
	"""
	page_title = ("Hotel Management System")  # For page title as well as heading
	rooms = Room.objects.all()
	for r in rooms:
		t = r.reservation_set.filter(valid=True)
		flag = True
		for x in t:
			if x.expected_arrival_date <= date.today() <= x.expected_departure_date:
				flag = False
				break
		r.availability = flag
	total_num_rooms = Room.objects.all().count()
	available_num_rooms = Room.objects.exclude(availability=False).count()
	return render(
		request,
		'room_view.html',
		{
			'rooms': rooms,
			'total_num_rooms': total_num_rooms,
			'available_num_rooms': available_num_rooms,
		}
	)

@login_required(login_url = '/login/')
def reservation_form(request,username):
	username = request.user.username
	c = Customer.objects.get(username=username)
	avail_rooms = RoomType.objects.all()
	x = date.today().strftime('%Y-%m-%d')
	error = ""
	return render(
		request,
		'reservation_form.html',
		{
			'avail_rooms': avail_rooms,
			'customer':c,
			'error':error,
			'x' : x
		}
	)
@login_required(login_url = '/login/')
def reservation_ack(request,username):

	valid = True
	error = ""
	username = request.POST.get('username',False)
	c = Customer.objects.get(username=username)
	roomtype = request.POST.get('room_select',False)
	no_of_adults = request.POST.get('no_of_adults',False)
	no_of_child = request.POST.get('no_of_child',False)
	arrival_timestamp = request.POST.get('arrival_timestamp',False)
	departure_timestamp = request.POST.get('departure_timestamp',False)
	roomtype_obj = RoomType.objects.get(name=roomtype)
	dummyroom = Room.objects.get(room_no='D-101')
	rooms = roomtype_obj.room_set.all()
	flag = False
	for r in rooms:
		t = r.reservation_set.filter(valid=True)
		r1 = Reservation(reservation_id=0,customer=c,no_of_children=no_of_child,no_of_adults=no_of_adults,expected_arrival_date=arrival_timestamp,expected_departure_date=departure_timestamp,room_no=dummyroom,valid=False)
		r1.save()
		resr = Reservation.objects.get(reservation_id=0)
		if not check_overlap(resr,t):
			flag = True
			room_allocated = r
			resr.delete()
			break
		resr.delete()
	if arrival_timestamp>departure_timestamp :
		valid = False
		error = "Select departure date later than that of arrival date"
	elif arrival_timestamp < str(date.today()) :
		valid = False
		error = "Arrival date can't be in the past"
	elif not flag:
		valid = False
		error = "No rooms avaiable of this type for your dates"
	else:
		r1 = Reservation(reservation_id=get_id(),customer=c,no_of_children=no_of_child,no_of_adults=no_of_adults,expected_arrival_date=arrival_timestamp,expected_departure_date=departure_timestamp,room_no=room_allocated,valid=False)
		r1.save()
		print(r1)
		emailaddr = c.email
	return render(
		request,
		'reservation_ack.html',
		{
			'valid':valid,
			'error':error,
			'email':emailaddr,
		}
	)

@login_required(login_url = '/login/')
def reservation_view(request,username):
	c = Customer.objects.get(username=request.user.username)
	r = c.reservation_set.all()
	return render(
		request,
		'reservation_view.html',
		{
			'reservation': r,
		}
	)

@login_required(login_url = '/login/')
def reservation_management(request,username):
	if request.user.isStaff:
		try:
			c = Reservation.objects.filter(valid=False)
		except Reservation.DoesNotExist:
			c = None
		return render(
			request,
			'reservation_management.html',
			{
				'reservation': c,
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def reservation_decide(request,username):
	if request.user.isStaff:
		id_ = request.POST.get('id',False)
		action = request.POST.get('action',False)
		message = ""
		res1 = Reservation.objects.get(reservation_id=id_)

		if action == "accept":
			roomType = res1.room_no.room_type
			roomtype_obj = RoomType.objects.get(name=roomType)	
			rooms = roomtype_obj.room_set.all()
			flag = False
			for r in rooms:
				t = r.reservation_set.filter(valid=True)
				if not check_overlap(res1,t):
					flag = True
					room_allocated = r
					break
			if flag:
				res1.room_no = room_allocated
				res1.valid = True
				res1.save()
				message = "Reservation Successful"
			else:
				message = "Overlap in reservation"
		elif action == "delete":
			message = "Deleted Successfully"
			r.delete()
		return render(
			request,
			'reservation_decide.html',
			{
				'message':message
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def room_status(request,roomNo):
	if request.user.isStaff:
		room = Room.objects.get(room_no=roomNo)
		t = room.reservation_set.filter(valid=True).exclude(expected_departure_date__lt=date.today())
		return render(
			request,
			'room_status.html',
			{
				'roomNo': roomNo,
				'res':t,	
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def active_resr(request):
	if request.user.isStaff:
		t = Reservation.objects.filter(valid=True,expected_departure_date__gte=date.today(),expected_arrival_date__lte=date.today())
		return render(
			request,
			'active_resr.html',
			{
				'res':t,	
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def reservation_change(request):
	if request.user.isStaff:
		t = Reservation.objects.filter(valid=True).exclude(expected_departure_date__lt=date.today())
		return render(
			request,
			'reservation_change.html',
			{
				'res':t,	
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def res_view(request,res_id):
	if request.user.isStaff:
		t = [Reservation.objects.get(reservation_id=res_id)]
		return render(
			request,
			'reservation_change.html',
			{
				'res':t,	
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def res_del(request,res_id):
	if request.user.isStaff and request.POST.get('action',False) == 'delete':
		res = Reservation.objects.get(reservation_id=res_id)
		res.delete()
		message = "Deleted Successfully"
		return render(
			request,
			'res_ack.html',
			{
				'message':message,	
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def res_edit(request,res_id):
	if request.user.isStaff and request.POST.get('action',False) == 'change':
		res = Reservation.objects.get(reservation_id=res_id)
		avail_rooms = RoomType.objects.all()
		x = res.expected_arrival_date.strftime('%Y-%m-%d')
		y = res.expected_departure_date.strftime('%Y-%m-%d')
		return render(
			request,
			'change_form.html',
			{
				'res' : res,
				'avail_rooms': avail_rooms,	
				'x' : x,
				'y' : y,
			}
		)
	return HttpResponse("Permission Denied.")

@login_required(login_url = '/login/')
def res_ack(request,res_id):
	if request.user.isStaff:
		id_ = request.POST.get('id',False)
		message = ""
		res1 = Reservation.objects.get(reservation_id=id_)
		res2 = copy.deepcopy(res1)
		res1.delete()
		res2.save()
		username = request.POST.get('username',False)
		c = Customer.objects.get(username=username)
		roomtype = request.POST.get('room_select',False)
		no_of_adults = request.POST.get('no_of_adults',False)
		no_of_child = request.POST.get('no_of_child',False)
		arrival_timestamp = request.POST.get('arrival_timestamp',False)
		departure_timestamp = request.POST.get('departure_timestamp',False)
		roomtype_obj = RoomType.objects.get(name=roomtype)
		dummyroom = Room.objects.get(room_no='D-101')
		rooms = roomtype_obj.room_set.all()
		flag = False
		for r in rooms:
			t = r.reservation_set.filter(valid=True)
			r1 = Reservation(reservation_id=0,customer=c,no_of_children=no_of_child,no_of_adults=no_of_adults,expected_arrival_date=arrival_timestamp,expected_departure_date=departure_timestamp,room_no=dummyroom,valid=False)
			r1.save()
			resr = Reservation.objects.get(reservation_id=0)
			if not check_overlap(resr,t):
				flag = True
				room_allocated = r
				resr.delete()
				break
			resr.delete()
		if arrival_timestamp>departure_timestamp :
			res2.save()
			message = "Select departure date later than that of arrival date"
		elif arrival_timestamp < str(date.today()) :
			res2.save()
			message = "Arrival date can't be in the past"
		elif not flag:
			res2.save()
			message = "No rooms avaiable of this type for your dates"
		else:
			r1 = Reservation(reservation_id=res2.reservation_id,customer=res2.customer,no_of_children=no_of_child,no_of_adults=no_of_adults,expected_arrival_date=arrival_timestamp,expected_departure_date=departure_timestamp,room_no=room_allocated,valid=True)
			r1.save()
			message = "Reservation Changed Successfully"
		return render(
			request,
			'res_ack.html',
			{
				'message':message
			}
		)
	return HttpResponse("Permission Denied.")