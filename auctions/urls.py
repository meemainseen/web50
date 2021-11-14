from django.urls import path
from .views import HomeView, ListingView, CreateListing, EditListing, DeleteListing, AddCategory, CategoryView, CategoryListView, login_view, logout_view, register, WatchView, WatchListView, PlaceBidView, BidHistoryView, CloseAuctionView, AuctionSummaryView

urlpatterns = [
    #path("", views.index, name="index"),
    path("", HomeView.as_view(), name="index"),
    path("view_listing/<int:pk>", ListingView.as_view(), name="view_listing"),
    path("create_listing/", CreateListing.as_view(), name="create_listing"),
    path("view_listing/edit/<int:pk>", EditListing.as_view(), name="edit_listing"),
    path("view_listing/<int:pk>/delete", DeleteListing.as_view(), name="delete_listing"),
    path('add_category', AddCategory.as_view(), name='add_category'),
    path('category/<str:cats>/', CategoryView, name='category'),
    path('category_list', CategoryListView, name='category_list'),
    path('watch/<int:pk>', WatchView, name='watch'),
    path('watchlist', WatchListView, name='watchlist'),
    path('view_listing/<int:pk>/bid', PlaceBidView, name='place_bid'),
    path('view_listing/<int:pk>/bid_history', BidHistoryView.as_view(), name='bid_history'),
    path('view_listing/<int:pk>/close_auction', CloseAuctionView, name='close_auction'),
    path('view_listing/<int:pk>/auction_summary', AuctionSummaryView.as_view(), name='auction_summary'),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
]
