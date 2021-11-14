from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.base import Model
from django.db.models.fields import related
from django.db.models.fields.related import ManyToManyField
from django.urls import reverse, reverse_lazy
from datetime import datetime, date
from django.db.models import Min, Max, Avg, Sum


class User(AbstractUser):
    pass


class Listing(models.Model):
    #id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    #title_tag = models.CharField(max_length=255)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    time_posted = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, default='Tech')
    watch = ManyToManyField(User, related_name='watch')
    image = models.ImageField(null=True, blank=True, upload_to = "images/")
    list_price = models.DecimalField(max_digits=5, decimal_places=2, default=0.99)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title + ' | ' + str(self.seller)

    def get_absolute_url(self):
        return reverse('view_listing', args=(str(self.id)))
    

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        #return reverse('view_listing', args=(str(self.id)))
        return reverse('index')

class Comments(models.Model):
    comment_text = models.TextField(default="default comment", null=True, blank=True)

class Bids(models.Model):
    listing = models.ForeignKey(Listing, related_name='bids', on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(User, related_name='bidder', on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    time_added = models.DateTimeField(auto_now=True)
    message = models.TextField(default="default message", null=True, blank=True)

    def __str__(self):
        return str(self.listing) + ' | ' + str(self.bidder)

    def get_absolute_url(self):
        #return reverse('view_listing', args=(str(self.listing.id)))
        return reverse('index')
    
    #def current_bid(self):
        #return self.aggregate(Max('amount'))


