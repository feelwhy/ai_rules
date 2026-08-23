---
id: 18-xml-translate-html
description: Never let xml_translate emit self-closing non-void HTML (empty FA icons break pages)
apply: always
---

# xml_translate HTML — never self-close non-void tags

Odoo `xml_translate` serializes a truly empty `<i></i>` / `<span></span>` as `<i/>` / `<span/>`. HTML5 ignores the `/`, so the tag stays open and **swallows the rest of the page** — including `en_US`. Incident 2026-08-23: app pages on faotools.com rendered as leftover icon glyphs.

## Hard ban (English source, TM, MCP, QWeb, defaults)

Never write:

- `<i class="fa …"/>`
- `<i class="fa …"></i>` (empty pair)
- empty `<span></span>`, `<b></b>`, `<em></em>` used as icons/wrappers

Always keep a space inside the pair:

```html
<i class="fa fa-plus text-success mr8"> </i>
```

Same for any other non-void wrapper. Void tags (`<br/>`, `<img/>`) stay void.

## After every xml_translate write

1. Close English with `close_self_closing_html` (`me_check_xml` / `validators`). The loader `_write_xml` must do this **after** `update_field_translations` — that call is what re-opens the hole.
2. Do not run TM `_apply_all` without closing English again (`close_live_html_void.py`).
3. App-page QWeb must use `safe_website_markup`, never raw `Markup()`, so a leftover `<i/>` cannot ship in HTML.

## Tests that must stay green

- `support_translations:TestXmlTranslateHtml`
- `modules_website:TestSafeWebsiteMarkup`
- `modules_website:TestAppPageFaqHttp`
- `validators` `html_void` / `check_html_structure`

A change that reintroduces empty `<i></i>` or drops the post-apply closer has failed, even if the Russian page still looks fine.
