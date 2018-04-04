from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# from django.urls import reverse
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import AbstractUser



class Customer(models.Model):
	name = models.CharField(max_length=200,default="",blank=True)
	username = models.CharField(max_length=15,default="", primary_key=True)
	phoNo = models.CharField(max_length=10,default="")
	def __str__(self):
		return str(self.username)

class Reservation(models.Model):
    reservation_id = models.PositiveSmallIntegerField(default=0,primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    no_of_children = models.PositiveSmallIntegerField(default=0)
    no_of_adults = models.PositiveSmallIntegerField(default=1)
    expected_arrival_date= models.DateField(default=date.today)
    expected_departure_date = models.DateField(default=date.today)
    room_no = models.ForeignKey('Room', on_delete=models.CASCADE)
    valid = models.BooleanField(default=False)
    class Meta:
        permissions = (('can_view_reservation', 'Can view reservation'),
                       ('can_view_reservation_detail', 'Can view reservation detail'),)

    # def get_absolute_url(self):
    #     return reverse('reservation-detail', args=str([self.reservation_id]))

    def __str__(self):
        return '%s %s %s %s %s' % (self.reservation_id, self.customer.name,self.expected_arrival_date,self.expected_departure_date, self.pk)


class Room(models.Model):
    room_no = models.CharField(max_length=10, primary_key=True)
    room_type = models.ForeignKey('RoomType', null=False, blank=True, on_delete=models.CASCADE)
    availability = models.BooleanField(default=True)
    # reservation = models.ForeignKey(Reservation, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['room_no', ]
        permissions = (('can_view_room', 'Can view room'),)

    def __str__(self):
        return "%s - %s - Rs. %i" % (self.room_no, self.room_type.name, self.room_type.price)


class RoomType(models.Model):
    name = models.CharField(max_length=25)
    price = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

class User(AbstractUser):
    isStaff = models.BooleanField(default=False)