# Data model: Fundação

## Models base (abstratos, `apps/core/models.py`), portados do padrão interno

| Model | Campos | Regra |
|---|---|---|
| `CleanSaveModel` | — | `save()` chama `full_clean()` |
| `TimeStampedModel` | `created_at`, `updated_at` | |
| `UUIDTimeStampedModel` | `id` UUID (PK) + timestamps | Usado por `Quote` |
| `ActiveModel` | `active` (bool, default True, indexado) | Soft toggle; sem soft delete |

> Catálogo usa PK inteira (`BigAutoField`); UUID fica para leads (`Quote`), cujo identificador aparece para o cliente.

## SiteConfiguration (singleton, `pk=1`)

| Campo | Tipo | Default |
|---|---|---|
| `site_name` | char 120 | "Irrigação Sem Fronteiras" |
| `short_name` | char 40 | "ISF" |
| `topbar_left`, `tagline` | char | `[DEFINIR]` |
| `footer_about` | text | `[DEFINIR]` |
| `whatsapp_number` | char 20 (só dígitos, com DDI) | "" (vazio → `[DEFINIR]` e links de WhatsApp levam a `/contato/`) |
| `phone_display` | char 30 | `[DEFINIR]` |
| `contact_email` | email | "" |
| `quote_recipient_emails` | text (um por linha) | "" |
| `address`, `cnpj`, `business_hours` | text/char | `[DEFINIR]` |
| `instagram_url`, `facebook_url`, `linkedin_url`, `youtube_url` | url | "" (LinkedIn = página pública da empresa) |
| `collections_label` | char 40 | "Coleções" |
| `whatsapp_default_message`, `quick_quote_message`, `category_help_message` | text | mensagens padrão com placeholders `{categoria}`, `{produto}` |
| `gtm_id`, `meta_pixel_id` | char 30 | "" |
| `default_meta_description` | char 160 | texto genérico |
| `default_og_image` | image | vazio |

Validação: `whatsapp_number` só dígitos (10–13); `gtm_id` `GTM-XXXX`; `meta_pixel_id` só dígitos.
