from django.contrib import admin
from react.models import Category, Poll, PollOption, Vote

# Register the question model
admin.site.register(Category)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(Vote)
