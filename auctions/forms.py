from django import forms
from django.forms import widgets
from .models import Listing, Category, Bids, Comments
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget

#cats = [('Electronics', 'Electronics'), ('Computers', 'Computers'), ('Home', 'Home'),]

cats = Category.objects.all().values_list('name', 'name')

cat_list = []

for cat in cats:
    cat_list.append(cat)

class PostForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'seller', 'category', 'description', 'image', 'list_price', 'end_time')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'title of your listing'}),
            #'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'choose a title tag for your listing'}),
            # Additional attributes are applied to seller field to be used in javascript snippet on Create Listing page, ensuring that
            # the created listing is posted against the logged on user
            'seller': forms.TextInput(attrs={'class': 'form-control', 'id': 'sellerID', 'value':'', 'type': 'hidden'}),
            'category': forms.Select(choices=cat_list, attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'list_price' : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'CAD $'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'bidTime', 'placeholder': 'Bidding ends at date/time'}),
            #'end_time': forms.AdminTimeWidget(attrs={'class': 'form-control', 'id': 'bidTime', 'placeholder': 'Bidding ends at date/time'})
        }

class EditForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'category', 'description', 'image', 'list_price', 'end_time')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'edit title of your listing'}),
            #'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'edit title tag of your listing'}),
            'category': forms.Select(choices=cat_list, attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'list_price' : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'CAD $'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'bidTime', 'placeholder': 'Bidding ends at date/time'}),
            #'end_time': forms.SplitDateTimeWidget(attrs={'class': 'form-control', 'id': 'bidTime', 'placeholder': 'Bidding ends at date/time'})
      
        }

class PlaceBidForm(forms.ModelForm):
    class Meta:
        model = Bids 
        fields = ('amount', 'message')

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Please enter a value greater than List Price / Current Bid'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
        }
    #def clean_bid(self):
        #bid = self.cleaned_data['amount']
        #return bid

