from django.contrib import admin

from apps.conteudo.models import (
    Banner,
    FAQItem,
    Highlight,
    HowItWorksStep,
    Page,
    PageSection,
    PortfolioItem,
    SectionText,
    Testimonial,
)  # fmt: skip


@admin.register(SectionText)
class SectionTextAdmin(admin.ModelAdmin):
    list_display = ("key", "kicker", "title")
    ordering = ("key",)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "order", "is_demo")
    list_editable = ("active", "order")


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("title", "placement", "icon", "active", "order")
    list_editable = ("active", "order")
    list_filter = ("placement",)


@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "order")
    list_editable = ("active", "order")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "tall", "featured", "active", "order", "is_demo")
    list_editable = ("tall", "featured", "active", "order")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "role", "rating", "authorized", "active", "order")
    list_editable = ("authorized", "active", "order")
    readonly_fields = ()
    help_texts = {}


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "placement", "active", "order")
    list_editable = ("active", "order")
    list_filter = ("placement",)


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0
    fields = ("order", "title", "anchor", "body")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "kind", "active", "updated_at")
    list_filter = ("kind", "active")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PageSectionInline,)
