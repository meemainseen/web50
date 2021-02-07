from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<title>/", views.entry, name="entry"),
    path("new", views.new, name="new"),
    path("search", views.search, name="search"),
    path("edit/<title>", views.edit, name="edit"),
    path("shuffle", views.shuffle, name="shuffle")
]
