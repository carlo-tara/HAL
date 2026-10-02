# Playbook — taglio DUP L2 (da `/sync <`)

Dopo un report `/sync <`, applicare **solo** con conferma e RGR nel repo consumer (o L1 in HAL se promozione).

## Priorità

1. **DUP** — tagliare body L2; lasciare puntatore al padre L1/L0  
2. **L1** con evidenza ≥2 progetti — promuovere canone; L2 resta delta path/brand  
3. **NEED-N** — non promuovere finché non c’è 2° sito o conferma esplicita  
4. **L2** path/brand/metriche sito — nessuna promozione  

## SEO/GEO (pattern noti)

| Azione | Dove |
|--------|------|
| Tagliare companion editoriale grasso | `liberating.it` `seo-geo-specialist` → stub + `seozoom-liberating` |
| Spezzare monolite | `piratesstraps` `seo-geo-specialist` → `seozoom-piratesstraps` + thin editorial |
| Off-chain → `extends: a-seozoom` | `the-verde.it` `seo-geo-expert` — **fatto** (verificare body thin vs L1) |
| Rimuovere copia voice fuori posto | `GiocoStrategico` `liberating-tone-of-voice` (identica a liberating.it; usare `gioco-strategico-voice`) |
| Modello sano | GiocoStrategico `role: data` + `role: editorial` |

## UI/UX

| Azione | Dove |
|--------|------|
| Tagliare DUP UI verso L1 | L2 `uiux-*` / `uiux-designer` → puntatori `a-uiux` (stack/a11y/layout già L1; extension-template) |
| Tagliare microcopy DUP | `WTP_App` `b2b-explorer-ui-ux` → puntatore `a-copywriter` § Microcopy UI (delta chrome/cluster ok) |
| Chart rules | rimando `a-charts` da UI L2 |

## Procedura RGR per ogni taglio

1. `/slice` nel **repo target** (acceptance: “rimuovere sezione X; puntatore Y”)  
2. `/red` — check greppabile che fallisce se il grasso è ancora lì (o test link)  
3. `/green` — edit minimo + version/CHANGELOG  
4. `/refactor` — anti-grasso residuo  
5. `make ready-for-review` se il repo ha Platform API  

**Repo target senza git o senza Makefile** (es. consumer solo-file): il gate Make è **N/A**, non “verde”. Chiudi il nodo con check greppabili (path assente, `role:` presente, righe sotto soglia, link riparati) e annota `make_exit: N/A` in progress; il commit resta assente finché il repo non viene versionato. Il `ready-proof` di HAL non osserva i path consumer (solo `a-*/` e `.cursor/skills/` locali).

Non eseguire dump multi-repo in un solo Act.
