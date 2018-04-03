from django.contrib import admin
from .models import *

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'username',
        'phoNo',
    )
    search_fields = [
        'username',
        'name',
        'phoNo',
    ]

    fieldsets = (
        (None, {
            'fields': (('name', 'username'),)
        }),
        ('Contact Information', {
            'fields': (('phoNo',None))
        })
    )

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'reservation_id',
        'customer',
        'no_of_children',
        'no_of_adults',
        'reservation_date_time',
        'expected_arrival_date_time',
        'expected_departure_date_time',
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_no',
        'room_type',
        'reservation',
        'availability',
    )
    # Adding filter
    list_filter = ('room_type', 'availability')
    fields = (('room_no', 'room_type'), 'reservation')

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

# Register your models here.
