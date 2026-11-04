from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Identidade"), {"fields": ("site_name", "short_name", "topbar_left", "tagline", "footer_about")}),
        (
            _("Contatos"),
            {
                "fields": (
                    "whatsapp_number",
                    "phone_display",
                    "contact_email",
                    "quote_recipient_emails",
                    "address",
                    "cnpj",
                    "business_hours",
                )
            },
        ),
        (_("Redes sociais"), {"fields": ("instagram_url", "facebook_url", "linkedin_url", "youtube_url")}),
        (
            _("Mensagens e rótulos"),
            {
                "fields": (
                    "collections_label",
                    "whatsapp_default_message",
                    "quick_quote_message",
                    "category_help_message",
                    "product_quick_quote_message",
                    "blog_enabled",
                )
            },
        ),
        (_("SEO e analytics"), {"fields": ("default_meta_description", "default_og_image", "gtm_id", "meta_pixel_id")}),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteConfiguration.objects.first() or SiteConfiguration.load()
        if not obj.pk or not SiteConfiguration.objects.filter(pk=obj.pk).exists():
            obj.save()
        return redirect(reverse("admin:core_siteconfiguration_change", args=[obj.pk]))
