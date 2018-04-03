from django.core.management.base import BaseCommand
from hotel.models import *
from django.contrib.auth.models import Group
import datetime
class Command(BaseCommand):
	args = '<foo bar ...>'
	help = 'our help string comes here'

	def _create_users(self):
		password = "1234"
		username = "PINU"
		user = User.objects.create_user(username=username,password=password)
		user.save()
		customer = Customer(username=username,name="Pratik Bhangale")
		customer.save()
		username = "TEST"
		user = User.objects.create_user(username=username,password=password)
		user.save()
		customer = Customer(username=username,name="testuser")
		customer.save()


		roomtype1 = RoomType(name="AC",price="900")
		roomtype1.save()
		roomtype2 = RoomType(name="NON-AC",price="500")
		roomtype2.save()

		room1 = Room(room_no="D-101",room_type=roomtype1)
		room1.save()
		room2 = Room(room_no="D-121",room_type=roomtype2)
		room2.save()

	def handle(self, *args, **options):
		self._create_users()
