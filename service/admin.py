from django.contrib import admin
from django.contrib.auth.models import Permission
from service.models import Kafic, Opstina


class KaficAdmin(admin.ModelAdmin):
    fields = ('naziv', 'adresa', 'opstina', 'vlasnik',)
    readonly_fields = ()
    def queryset(self, request):

        qs = super(KaficAdmin, self).queryset(request)
        if request.user.is_superuser:
            # It is mine, all mine. Just return everything.
            return qs
        # Now we just add an extra filter on the queryset and
        # we're done. Assumption: Page.owner is a foreignkey
        # to a User.
        return qs.filter(vlasnik=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            self.readonly_fields = ('vlasnik',)
            return True


    # to disable editing for specific or all fields
    # you can use readonly_fields attribute
    # (to see data you need to remove editable=False from fields in model):




admin.site.register(Permission)
admin.site.register(Kafic, KaficAdmin)
admin.site.register(Opstina)
