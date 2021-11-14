import decimal
from typing import Container, List
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import request
from django.http.request import validate_host
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import User, Listing, Category, Bids, Comments
from .forms import PostForm, EditForm, PlaceBidForm
from django.core.exceptions import ValidationError
from django.db.models import Max, Min, Avg, Sum
from decimal import Decimal
from django.contrib import messages

#def index(request):
    #return render(request, "auctions/index.html")

# Homepage view with a list of all listings
class HomeView(ListView):
    model = Listing
    template_name = 'auctions/index.html'
    ordering = ['-time_posted']
    #ordering = ['-id']
    #creating a category dropdown menu which will be avaialable at homepage
    def get_context_data(self, *args, **kwargs):
        cat_dropdown = Category.objects.all()
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context["cat_dropdown"] = cat_dropdown
        return context
    
# Individual listing view with details on listing item links to view/place bids and add/remove to watchlist
class ListingView(DetailView):
    model = Listing
    template_name = 'auctions/view_listing.html'
    
    def get_context_data(self, *args,**kwargs):
        listing = get_object_or_404(Listing, id=self.kwargs['pk'])
        list_price = str(round(listing.list_price, 2))
        bid_item = (Bids.objects.filter(listing=listing))
        # Creating context data for the listing page to display Current Bid if exists, else the list price
        if bid_item.exists():
            current_bid = str(round(bid_item.aggregate(Max('amount'))['amount__max'], 2))
        else:
            current_bid = list_price

        total_bids = bid_item.count()
        # Creating context for adding / removing listing from Watchlist, btn status on the page.
        watched = False
        if listing.watch.filter(id=self.request.user.id).exists():
            watched = True
        context = super(ListingView, self).get_context_data(*args, **kwargs)
        context["watched"] = watched
        context["current_bid"] = current_bid
        context["list_price"] = list_price
        context["total_bids"] = total_bids
        return context

# Note the name of the button gets mentioned in requeset.POST.get method
# HttpResponseRedirect methos is used here to keep the user on the same post page
def WatchView(request, pk):
    listing = get_object_or_404(Listing, id=request.POST.get("watch_btn"))
    # Setting up button state for adding to and removing a listing from watchlist
    watched = False
    if listing.watch.filter(id=request.user.id).exists():
        listing.watch.remove(request.user)
        watched = False
    else:
        listing.watch.add(request.user)
        watched =True
    return HttpResponseRedirect(reverse('view_listing', args=[str(pk)]))

# View where users can watch all items added to their watchlist
def WatchListView(request):
    watchlist = Listing.objects.filter(watch=request.user.id)
    return render(request, 'auctions/watchlist.html', {'watchlist': watchlist})


# View to Create New Listing
class CreateListing(CreateView):
    model = Listing
    form_class = PostForm
    template_name = 'auctions/create_listing.html'
    #fields = '__all__'
    #fields = ('title', 'title_tag', 'description')
    success_url = reverse_lazy('index')

# View to edit / update existing listing
class EditListing(UpdateView):
    model = Listing
    template_name = 'auctions/edit_listing.html'
    form_class = EditForm
    #fields = ['title', 'title_tag', 'description']
    success_url = reverse_lazy('index')

# View to Delete existing listing
class DeleteListing(DeleteView):
    model = Listing
    template_name = 'auctions/delete_listing.html'
    success_url = reverse_lazy('index')

# Creating category list view to be available on pages where category dropdown is not available
def CategoryListView(request):
    cat_list = Category.objects.all()
    return render(request, 'auctions/category_list.html', {'cat_list': cat_list})

#cats comes from url.py file -> path('category/<str:cats>/', CategoryView, name='category'),
def CategoryView(request, cats):
    #category in the filter comes from the Post Model -> category = models.CharField(max_length=255, default='coding')
    category_listings = Listing.objects.filter(category=cats.title().replace('-', ' '))
    return render(request, 'auctions/categories.html', {'cats':cats.title().replace('-', ' '), 'category_listings':category_listings})

# View to add a category
class AddCategory(CreateView):
    model = Category
    #form_class = PostForm
    template_name = 'auctions/add_category.html'
    fields = '__all__'

# View to place bid on selected listing
def PlaceBidView(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    list_price = str(round(listing.list_price, 2))
    list_price_value = float(list_price)
    bid_item = Bids.objects.filter(listing=listing)
    # If there are bids placed on the listing fetch the maximum bid value
    if bid_item.exists():
        current_bid = str(round(bid_item.aggregate(Max('amount'))['amount__max'], 2))
    # If no bids placed then list price will be taken as current bid
    else:
        current_bid = list_price
    current_bid_value = float(current_bid)

    # Accessing values submitted via PlaceBidForm
    if request.method == "POST":
        form = PlaceBidForm(request.POST)
        if form.is_valid():
            bid_value = form.cleaned_data['amount']
            context = {
                'listing': listing,
                'list_price': list_price,
                'current_bid': current_bid,
                'form': form
            }
            # If entered bid value is less than or equal to the list price (where no bids placed yed) return an error
            if bid_value <= list_price_value:
                return render(request, "auctions/place_bid.html", {
                "message": "Please enter an amount greater than List Price", "listing": listing, "list_price": list_price, "current_bid": current_bid, "form": form
                })
            
            # If entered bid value is less than or equal to the maximum bid value (where there are bids on the listing) return an error
            elif bid_value <= current_bid_value:
                return render(request, "auctions/place_bid.html", {
                "message": "Please enter an amount greater than Current Bid.", "listing": listing, "list_price": list_price, "current_bid": current_bid, "form": form
                })
            # Update the values submitted via PlaceBidForm
            else:
                data = Bids()
                data.bidder = request.user
                data.listing = listing
                data.amount = form.cleaned_data['amount']
                data.message = form.cleaned_data['message']
                data.save()
                messages.success(request, 'Success! Your Bid is now the Current Bid')
                #return HttpResponseRedirect(reverse_lazy('view_listing', args=[str(pk)]))
                return HttpResponseRedirect(reverse_lazy('bid_history', args=[str(pk)]))
    
    # If request method is not POST load the PlaceBidForm
    form = PlaceBidForm()
    context = {
        'listing': listing,
        'list_price': list_price,
        'current_bid': current_bid,
        'form': form
    }
    return render(request, 'auctions/place_bid.html', context)

# View to access bid history on a list item
class BidHistoryView(CreateView):
    model = Bids
    fields = '__all__'
    template_name = 'auctions/bid_history.html'
    ordering = ['-time_added']   
    def get_context_data(self, **kwargs):
        listing = get_object_or_404(Listing, id=self.kwargs['pk'])
        list_price = str(round(listing.list_price, 2))
        bid_item = Bids.objects.filter(listing=listing)
        total_bids = bid_item.count()
        # Obtaining queryset of all existing bids on the listing and arranging them in descending order by amount
        bid_dataset = listing.bids.all().order_by('-amount')
        if bid_item.exists():
            current_bid = str(round(bid_item.aggregate(Max('amount'))['amount__max'], 2))
        else:
            current_bid = list_price
        context = super().get_context_data(**kwargs)
        context ['bit_item'] = bid_item
        context ['total_bids'] = total_bids
        context ['listing'] = listing
        context ['list_price'] = list_price
        context ['current_bid'] = current_bid
        context ['bid_dataset'] = bid_dataset
        return context

# View to close auction on the listing.
def CloseAuctionView(request, pk):
    listing = get_object_or_404(Listing, id=pk)
    list_price = str(round(listing.list_price, 2))
    bid_item = Bids.objects.filter(listing=listing)
    if bid_item.exists():
        current_bid = str(round(bid_item.aggregate(Max('amount'))['amount__max'], 2))
    else:
        current_bid = list_price

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing.id)
        listing.is_active = False
        listing.save()
        messages.success(request, 'Auction on this item is now closed.')
        return HttpResponseRedirect(reverse('auction_summary', args=[str(pk)]))

    return render(request, 'auctions/close_auction.html', {'listing': listing, 'list_price': list_price, 'current_bid': current_bid})

# View to present summary of the auction on the listing. User is taken here after the auction is closed.
class AuctionSummaryView(DetailView):
    model = Listing
    template_name = 'auctions/auction_summary.html'
    ordering = ['-time_added']   
    def get_context_data(self, **kwargs):
        listing = get_object_or_404(Listing, id=self.kwargs['pk'])
        bid_item = Bids.objects.filter(listing=listing)
        total_bids = bid_item.count()
        # Obtaining queryset of all existing bids on the listing and arranging them in descending order by amount
        bid_dataset = listing.bids.all().order_by('-amount')
        closing_bid = bid_item.aggregate(Max('amount'))['amount__max']
        winning_bid = bid_dataset.get(amount=closing_bid)
        closing_bid_value = str(round(bid_item.aggregate(Max('amount'))['amount__max'], 2))
    
        context = super().get_context_data(**kwargs)
        context['listing'] = listing
        context ['bid_item'] = bid_item
        context ['total_bids'] = total_bids
        context ['closing_bid'] = closing_bid
        context ['closing_bid_value'] = closing_bid_value
        context ['winning_bid'] = winning_bid
        context ['bid_dataset'] = bid_dataset
        return context

# Login 
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

# Logout
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



    
    
    
    

    

