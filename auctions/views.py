from multiprocessing.forkserver import connect_to_new_process
from statistics import LinearRegression

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Model, Max
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.contrib import messages

from .models import User, Listing, Bid, Comment


class CreateListingForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField()
    image_src = forms.CharField(required=False)
    category = forms.CharField(required=False)
    start_amount = forms.DecimalField(min_value=0.1)

class CreateBidForm(forms.Form):
    amount = forms.DecimalField(min_value=0.1)

class CreateCommentForm(forms.Form):
    content = forms.CharField(min_length=1, max_length=500)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True).all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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


@login_required
def create(request: HttpRequest):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Listing.objects.create(
                title=data["title"],
                description=data["description"],
                image_src=data["image_src"] if data["image_src"] else None,
                start_amount=data["start_amount"],
                category=data["category"] if data["category"] else "Uncategorized",
                created_by=request.user,
            )
            return redirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })

    return render(request, "auctions/create.html", {
        "form": CreateListingForm(),
    })


@login_required
def watchlist(request: HttpRequest, id=None):
    if request.method == "POST":
        listing = Listing.objects.filter(pk=id).first()
        user = request.user
        if user not in listing.wishlisted_by.all():
            listing.wishlisted_by.add(user)
        else:
            listing.wishlisted_by.remove(user)
        return redirect(reverse("index"))
    else:
        return render(request, "auctions/watchlist.html", {
            "watchlist": Listing.objects.all()
        })

def listing(request, id):
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.filter(pk=id).first(),
        "bid_form": CreateBidForm(),
        "bids": Bid.objects.filter(listing=id).all(),
        "comment_form": CreateCommentForm(),
        "comments": Comment.objects.filter(listing=id).all()
    })

@login_required
def bid(request, id):
    if request.method == "POST":
        form = CreateBidForm(request.POST)
        if form.is_valid():
            listing = Listing.objects.filter(pk=id).first()
            max_bid = Bid.objects.filter(listing=listing).aggregate(max_amount=Max("amount"))["max_amount"]
            current_price = max_bid if max_bid else listing.start_amount

            amount = form.cleaned_data["amount"]
            if current_price > amount:
                messages.error(request, "Incorrect amount!")
                return redirect("listing", id=id)

            Bid.objects.create(
                amount=amount,
                created_by=request.user,
                listing=Listing.objects.filter(pk=id).first()
            )
    return redirect("listing", id=id)


@login_required
def comment(request: HttpRequest, id):
    if request.method == "POST":
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            listing = Listing.objects.filter(pk=id).first()
            Comment.objects.create(
                content=content,
                listing=listing,
                created_by=request.user
            )

    return redirect("listing", id=id)


@login_required
def close(request: HttpRequest, id):
    if request.method == "POST":
        listing = Listing.objects.filter(pk=id).first()
        if request.user == listing.created_by and listing.is_active:
            max_bid = Bid.objects.order_by("-amount").first()
            if max_bid:
                listing.winner = max_bid.created_by

            listing.is_active = False
            listing.save()
            messages.success(request, "Аукцион успешно закрыт.")

    return redirect("listing", id=id)


def categories(request: HttpRequest):
    return render(request, "auctions/categories.html", {
        "categories": (Listing.objects
            .exclude(category__isnull=True)
            .exclude(category="")
            .order_by("category")
            .values_list("category", flat=True)
            .distinct())
    })


def category(request: HttpRequest, category):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(category=category)
    })