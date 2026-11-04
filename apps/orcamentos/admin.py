import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from apps.orcamentos.choices import QuoteStatus
from apps.orcamentos.models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    can_delete = False
    fields = ("quantity", "unit", "product_name", "variant_label", "product_sku", "variant_sku", "product")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("code", "created_at", "name", "company", "city", "state", "source", "status", "n_itens", "email_ok")
    list_filter = ("status", "source", "created_at", "state")
    list_editable = ("status",)
    search_fields = ("code", "name", "company", "email", "phone", "city", "items__product_name", "items__product_sku")
    date_hierarchy = "created_at"
    inlines = (QuoteItemInline,)
    readonly_fields = (
        "code",
        "created_at",
        "updated_at",
        "source",
        "consent",
        "consent_text",
        "email_sent_at",
        "email_error",
    )
    fieldsets = (
        (None, {"fields": ("code", "status", "source", "created_at", "updated_at")}),
        (_("Contato"), {"fields": ("name", "company", "email", "phone", "city", "state", "message")}),
        (_("Atendimento"), {"fields": ("internal_notes",)}),
        (
            _("LGPD e e-mail"),
            {"fields": ("consent", "consent_text", "email_sent_at", "email_error"), "classes": ("collapse",)},
        ),
    )
    actions = ("marcar_em_atendimento", "marcar_respondido", "marcar_fechado", "marcar_perdido", "exportar_csv")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("items")

    def has_add_permission(self, request):
        return False

    @admin.display(description=_("itens"))
    def n_itens(self, obj):
        return len(obj.items.all())

    @admin.display(description=_("e-mail"), boolean=True)
    def email_ok(self, obj):
        return bool(obj.email_sent_at) and not obj.email_error

    def _status(self, request, queryset, status):
        n = queryset.update(status=status)
        self.message_user(
            request, _("%(n)d orçamento(s) marcado(s) como %(s)s.") % {"n": n, "s": QuoteStatus(status).label}
        )

    @admin.action(description=_("Marcar como em atendimento"))
    def marcar_em_atendimento(self, request, queryset):
        self._status(request, queryset, QuoteStatus.IN_PROGRESS)

    @admin.action(description=_("Marcar como respondido"))
    def marcar_respondido(self, request, queryset):
        self._status(request, queryset, QuoteStatus.ANSWERED)

    @admin.action(description=_("Marcar como fechado (ganho)"))
    def marcar_fechado(self, request, queryset):
        self._status(request, queryset, QuoteStatus.CLOSED)

    @admin.action(description=_("Marcar como perdido"))
    def marcar_perdido(self, request, queryset):
        self._status(request, queryset, QuoteStatus.LOST)

    @admin.action(description=_("Exportar CSV (um item por linha)"))
    def exportar_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="orcamentos.csv"'
        resp.write("﻿")
        w = csv.writer(resp, delimiter=";")
        w.writerow(["codigo", "data", "status", "origem", "nome", "empresa", "email", "telefone", "cidade", "uf",
                    "quantidade", "unidade", "produto", "variacao", "sku", "mensagem"])  # fmt: skip
        for q in queryset.prefetch_related("items"):
            for i in q.items.all() or [None]:
                w.writerow([q.code, q.created_at.strftime("%Y-%m-%d %H:%M"), q.get_status_display(), q.get_source_display(),
                            q.name, q.company, q.email, q.phone, q.city, q.state,
                            i.quantity if i else "", i.unit if i else "", i.product_name if i else "",
                            i.variant_label if i else "", i.sku if i else "", q.message])  # fmt: skip
        return resp
