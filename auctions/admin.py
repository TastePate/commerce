from django.contrib import admin

from auctions.models import Listing, User, Comment, Bid

admin.site.register(Listing)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Bid)
