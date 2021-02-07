from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from . import util
import markdown2
from django import forms
import random

# Form is defined using Django form class. Will be used in both adding new pages or updating the content of existing page
class NewEntryForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

# Home page takes a list of exsiting titles and iterates over the list to display in an unordered list
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    # If the title is not found in entries list, error page is displayed
    if not (util.get_entry(title)):
        return render(request, "encyclopedia/error.html", {
            "content": "404 Page not found."
        })
    # If title is found then the relevant content is displayed. Markdown2 filter is used to display the content.     
    else:
        content = markdown2.markdown(util.get_entry(title))
        return render(request, "encyclopedia/wiki/entry.html", {
            "title": title,
            "content": content
        })

def new(request):
    #Check if method is POST
    if request.method == "POST":
        #Take the data submitted by user
        form = NewEntryForm(request.POST)
        # Check validity (server-side)
        if form.is_valid():
            # Obtiain cleaned data
            title = form.cleaned_data["title"]
            entries = util.list_entries()
            # If an encyclopedia entry does not already exist
            if not title.upper() in map(str.upper, entries):
                #Getting the content from the form and encyclopedia entry saved on disk
                content = form.cleaned_data["content"]
                util.save_entry(title, content)
                # Redirect user to the new entry page
                display_content = markdown2.markdown(util.get_entry(title))
                return render(request, "encyclopedia/wiki/entry.html", {
                    "title": title,
                    "content": display_content
                })
            else:
                #Content will now reflect error message
                #content = "Error: This encyclopedia entry already exists"
                #Reidrect user to error page with content displayed
                return render(request, "encyclopedia/error.html", {
                    "content": "Error: This encyclopedia entry already exists"
                })
        # If the form is invalid, re-render the page with existing information
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    # if a GET or any other method, a blank form is created
    else: 
        form = NewEntryForm()
    return render(request, "encyclopedia/new.html", {
        "form": form
    })

def search(request):
    # getting the value put in search query
    if request.method == 'GET':
        title = request.GET.get('q')
        # initialize list of titles from pages in entries
        entries = util.list_entries()
        # if the search term is not exact match
        if not title.upper() in map(str.upper, entries):
            # getting a list of titles that matches the substring
            match = [i for i in entries if title in i]
            #if match list is empty
            if not match:
                return render(request, "encyclopedia/error.html", {
                    "content": "No entry found."
                })
            #user is redirected to the search page with entries showig from match list
            else:
                return render(request, "encyclopedia/search.html", {
                    "title": title,
                    "match": match
                })
        # if the query title is exact match user is directed to the entry page
        else:
            content = markdown2.markdown(util.get_entry(title))
            return render(request, "encyclopedia/wiki/entry.html", {
                "title": title,
                "content": content
            })


def edit(request, title):
    # If the request method is POST, the submitted data is obtained and processed
    if request.method == "POST":
        #Take the data submitted by user
        form = NewEntryForm(request.POST)
        # Check validity (server-side)
        if form.is_valid():
            # Obtiain cleaned data and update content area
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            # Redirect user to the new entry page
            display_content = markdown2.markdown(util.get_entry(title))
            return render(request, "encyclopedia/wiki/entry.html", {
                   "title": title,
                   "content": display_content
            })
        # If the form is invalid, re-render the page with existing information
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
    # If the request method is GET
    else:
        content = util.get_entry(title)
        # Initial values on the form are set to be existing values on the relevant entry page
        form = NewEntryForm(initial={
            'title': title,
            'content': content
        })
        # User is directed to the edit page, the content area preloaded with existing entry's detail
        return render(request, "encyclopedia/edit.html", {
            'title': title,
            'form': form
        })


def shuffle(request):
    # Obtaining a list of entries
    entries = util.list_entries()
    # A random entry is selected as title
    title = random.choice(entries)
    # The content of randomly picked title is obtained and filtered for display
    content = util.get_entry(title)
    display_conent = display_content = markdown2.markdown(util.get_entry(title))
    # Redirects user to the randomly selected entry page
    return render(request, "encyclopedia/wiki/entry.html", {
        "title": title,
        "content": display_conent
    })