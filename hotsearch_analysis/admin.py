from django.contrib import admin
from .models import HotSearchItem, WeiboItem

# Register your models here.
class HotSearchAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
class WeiboAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(HotSearchItem, HotSearchAdmin)
admin.site.register(WeiboItem, WeiboAdmin)