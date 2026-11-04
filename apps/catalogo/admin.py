from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from apps.catalogo.choices import ImportStatus
from apps.catalogo.forms import (
    CAMPOS_PRODUTO,
    PREFIXO,
    CategoryAdminForm,
    ProductAdminForm,
    _categoria_escolhida,
    form_de_variacao,
)
from apps.catalogo.models import CatalogImport, Category, Collection, Product, ProductImage, Variant
from apps.catalogo.services.importacao import ErroPlanilha, importar


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ("__str__", "order", "active", "show_on_home", "n_produtos", "n_atributos", "is_demo")
    list_editable = ("order", "active", "show_on_home")
    list_filter = ("active", "show_on_home", "is_demo", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("parent",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "parent", "icon", "image", "order", "active", "show_on_home", "is_demo")}),
        (_("Textos"), {"fields": ("description", "seo_text", "meta_title", "meta_description")}),
        (
            _("Atributos técnicos"),
            {
                "fields": ("attribute_schema", "atributos_herdados"),
                "description": _(
                    "Defina os atributos esperados nos produtos desta categoria. Cada item: "
                    "<code>key</code> (sem espaços), <code>label</code>, <code>type</code> "
                    "(text, number, boolean, choice), <code>unit</code>, <code>variant</code> (true = gera variação), "
                    "<code>required</code>, <code>choices</code> (lista, para choice). Subcategorias herdam do pai."
                ),
            },
        ),
    )
    readonly_fields = ("atributos_herdados",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent").annotate(_n=Count("primary_products"))

    @admin.display(description=_("produtos"), ordering="_n")
    def n_produtos(self, obj):
        return obj._n

    @admin.display(description=_("atributos"))
    def n_atributos(self, obj):
        return len(obj.attribute_schema or [])

    @admin.display(description=_("herdados do pai"))
    def atributos_herdados(self, obj):
        if not obj.parent_id or not obj.parent.attribute_schema:
            return "—"
        return ", ".join(a["label"] + (" (variação)" if a.get("variant") else "") for a in obj.parent.attribute_schema)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "period_label", "order_deadline", "featured", "is_main", "active", "order", "is_demo")
    list_editable = ("featured", "active", "order")
    list_filter = ("active", "featured", "is_demo")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "image", "color", "order", "active", "is_demo")}),
        (_("Período e prazo"), {"fields": ("starts_on", "ends_on", "order_deadline", "deadline_note")}),
        (_("Home"), {"fields": ("featured", "is_main")}),
        (_("SEO"), {"fields": ("seo_text", "meta_title", "meta_description")}),
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("previa", "image", "alt", "kind", "order")
    readonly_fields = ("previa",)

    @admin.display(description=_("prévia"))
    def previa(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="" style="width:64px;height:64px;object-fit:cover;border-radius:8px">', obj.card_url
            )
        return "—"


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        form = form_de_variacao(obj)
        kwargs["form"] = form
        kwargs["fields"] = list(form._meta.fields)
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def get_fields(self, request, obj=None):
        form = form_de_variacao(obj)
        nomes = [PREFIXO + a["key"] for a in (obj.variant_attributes if obj else [])]
        return [*nomes, *form._meta.fields]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "sku", "primary_category", "n_variacoes", "active", "featured", "novidade", "is_demo")
    list_filter = ("active", "featured", "is_demo", "sale_unit", "primary_category", "collections")
    list_editable = ("active", "featured")
    search_fields = ("name", "sku", "variants__sku")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("primary_category",)
    filter_horizontal = ("categories", "collections")
    inlines = (VariantInline, ProductImageInline)
    actions = ("ativar", "desativar", "marcar_destaque")
    list_per_page = 50
    save_on_top = True

    class Media:
        js = ("admin/js/produto_categoria.js",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("primary_category").annotate(_nv=Count("variants"))

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs["fields"] = CAMPOS_PRODUTO
        return super().get_form(request, obj, change=change, **kwargs)

    def get_fieldsets(self, request, obj=None):
        dados = request.POST if request.method == "POST" else None
        form = self.get_form(request, obj)(data=dados, instance=obj, initial=request.GET.dict() if not obj else None)
        categoria = _categoria_escolhida(form)
        nomes_attr = form.nomes_atributos
        if not categoria:
            descricao = _("Escolha a categoria principal: os campos da ficha técnica aparecem em seguida.")
        elif not nomes_attr:
            descricao = _("A categoria escolhida não define atributos de ficha. Defina-os em Catálogo › Categorias.")
        else:
            descricao = _("Campos definidos pela categoria %(cat)s.") % {"cat": categoria}
        return (
            (None, {"fields": ("name", "slug", "sku", "primary_category", "short_description", "description")}),
            (_("Ficha técnica"), {"fields": nomes_attr, "description": descricao}),
            (_("Venda"), {"fields": ("min_quantity", "quantity_step", "sale_unit")}),
            (
                _("Vitrine"),
                {"fields": ("active", "featured", "new_until", "relevance", "categories", "collections", "is_demo")},
            ),
            (_("SEO"), {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.ensure_primary_in_categories()

    @admin.display(description=_("variações"), ordering="_nv")
    def n_variacoes(self, obj):
        return obj._nv

    @admin.display(description=_("novidade"), boolean=True)
    def novidade(self, obj):
        return obj.is_new

    @admin.action(description=_("Ativar selecionados"))
    def ativar(self, request, queryset):
        self.message_user(request, _("%d produto(s) ativado(s).") % queryset.update(active=True))

    @admin.action(description=_("Desativar selecionados"))
    def desativar(self, request, queryset):
        self.message_user(request, _("%d produto(s) desativado(s).") % queryset.update(active=False))

    @admin.action(description=_("Marcar como destaque"))
    def marcar_destaque(self, request, queryset):
        self.message_user(request, _("%d produto(s) em destaque.") % queryset.update(featured=True))


@admin.register(CatalogImport)
class CatalogImportAdmin(admin.ModelAdmin):
    list_display = ("created_at", "file", "dry_run", "status", "summary", "created_by")
    list_filter = ("status", "dry_run")
    readonly_fields = ("status", "summary", "relatorio", "created_by", "created_at")
    actions = ("executar_de_verdade",)

    def get_fields(self, request, obj=None):
        if obj:
            return ("file", "dry_run", "status", "summary", "relatorio", "created_by", "created_at")
        return ("file", "dry_run")

    def has_change_permission(self, request, obj=None):
        return False if obj else super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)
        self._executar(request, obj, dry_run=obj.dry_run)

    def _executar(self, request, obj, *, dry_run: bool):
        try:
            relatorio = importar(obj.file.open("rb"), nome=obj.file.name, dry_run=dry_run)
        except ErroPlanilha as erro:
            obj.status, obj.summary, obj.report = ImportStatus.FAILED, str(erro)[:300], {"erro": str(erro)}
            obj.save()
            self.message_user(request, str(erro), messages.ERROR)
            return
        finally:
            obj.file.close()
        obj.status = ImportStatus.DONE
        obj.summary = relatorio.resumo()[:300]
        obj.report = relatorio.as_dict()
        obj.dry_run = dry_run
        obj.save()
        nivel = messages.SUCCESS if relatorio.ok else messages.WARNING
        self.message_user(request, relatorio.resumo(), nivel)

    @admin.action(description=_("Importar de verdade (repetir sem simulação)"))
    def executar_de_verdade(self, request, queryset):
        for obj in queryset:
            novo = CatalogImport.objects.create(file=obj.file, dry_run=False, created_by=request.user)
            self._executar(request, novo, dry_run=False)

    @admin.display(description=_("relatório"))
    def relatorio(self, obj):
        rep = obj.report or {}
        if "erro" in rep:
            return rep["erro"]
        linhas = [(e.get("linha") or "—", e.get("sku") or "", e.get("mensagem")) for e in rep.get("erros", [])]
        avisos = [(a.get("linha") or "—", a.get("sku") or "", a.get("mensagem")) for a in rep.get("avisos", [])]
        tabela = lambda itens, titulo: (  # noqa: E731
            format_html(
                "<h4>{} ({})</h4><table><thead><tr><th>Linha</th><th>SKU</th><th>Mensagem</th></tr></thead>"
                "<tbody>{}</tbody></table>",
                titulo,
                len(itens),
                format_html_join("", "<tr><td>{}</td><td>{}</td><td>{}</td></tr>", itens),
            )
            if itens
            else ""
        )
        return format_html(
            "<p><b>{}</b></p>{}{}", rep.get("resumo", ""), tabela(linhas, "Erros"), tabela(avisos, "Avisos")
        )
