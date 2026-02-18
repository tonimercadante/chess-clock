from django.contrib import admin

from games.models import Clocks, Types

# Register your models here.
admin.site.register([Clocks, Types])

