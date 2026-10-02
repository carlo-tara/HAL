# Brief progetto SEO — template

Compila questo file nel progetto target (es. `.cursor/seo/{nome-sito}.md`) o incorporalo nella skill figlia L2 (`extends: a-seozoom`).

---

## Identità

| Campo | Valore |
|-------|--------|
| Nome sito | |
| Dominio | |
| Working directory | |
| Tipo sito | statico / WordPress / altro |

---

## Credenziali `.env`

| Variabile | Valore / esempio |
|-----------|------------------|
| `SEOZOOM_USER` | email account SeoZoom |
| `SEOZOOM_PASSWORD` | password |
| `SEOZOOM_PROJECT` | nome progetto in SeoZoom |
| `SEOZOOM_PROJECT_COMPETITOR` | opzionale: altro progetto SeoZoom → `seozoom-competitor/` |
| `GOOGLE_APPLICATION_CREDENTIALS` | path service account JSON |
| `GSC_SITE_URL` | `sc-domain:esempio.it` o `https://esempio.it/` |
| `GA4_PROPERTY_ID` | ID numerico property |
| `GTM_CONTAINER_ID` | es. `GTM-XXXXXXX` |
| `CLOUDFLARE_API_TOKEN` | token Analytics:Read (opzionale) |
| `CLOUDFLARE_ZONE_ID` | zone ID (opzionale) |

---

## Path dati

| Path | Contenuto |
|------|-----------|
| Export SEO | `seo/YYMMDD/` (`seozoom/`, `seozoom-competitor/` se attivo, `google/`, `cloudflare/`, `substack/`) |
| Sitemap arricchita | `{path}/sitemap-enriched.json` |
| Contenuti | `{path content/}` |
| Tracker batch | `{path tracker, se usato}` |

---

## Dove intervenire (contenuti)

| Tipo pagina | Path / file | Note |
|-------------|-------------|------|
| | | |
| | | |

---

## Skill di progetto correlate

| Skill | Path | Ruolo |
|-------|------|-------|
| | `.cursor/skills/` | |
| | | |

---

## Comandi build / verifica

```bash
# Esempio — adatta al progetto
# cd {project-root} && {comando build}
# cd {project-root} && {comando audit}
```

---

## Regole locali

- 
- 
