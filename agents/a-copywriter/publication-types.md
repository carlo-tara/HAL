# Tipi di pubblicazione web

Template generici. Adatta tono, lessico e chiusura al brand file del progetto.

---

## Scheda prodotto

**Lunghezza:** 150–350 parole  
**Formato:** HTML (`<p>`, `<strong>`) o Markdown

### Struttura

```
1. Hook — nome [prodotto] + promessa (keyword primaria nel 1° paragrafo, 1 sola volta naturale)
2. Beneficio / materiale — cosa fa, di cosa è fatto, perché conta
3. Dettaglio — lavorazione, specifiche, differenziatori verificabili
4. Uso / compatibilità — contesto concreto, abbinamenti, limiti
5. Chiusura — pattern brand (es. «Scegliere [prodotto] significa…»)
```

### Template HTML

```html
<p>Il <strong>[nome prodotto]</strong> [hook + keyword naturale]. [Identità o stile in 1 frase].</p>

<p>[Beneficio principale]. Realizzato con <strong>[materiale/componente]</strong>, [dettaglio verificabile].</p>

<p>[Specifica tecnica o differenziatore]. [Dato concreto: misura, procedura, compatibilità].</p>

<p>[Contesto d'uso]. [Abbinamento o occasione specifica, non generica].</p>

<p>[Chiusura brand: pattern da brand file].</p>
```

---

## Categoria / archivio

**Lunghezza:** 200+ parole  
**Obiettivo:** answer-first per query di cluster + link interni

### Struttura

```
1. Definizione — cos'è questa categoria in 1–2 frasi (risposta diretta)
2. Per chi / quando — pubblico e situazioni concrete
3. Criteri di scelta — 2–3 elementi distintivi (no rule of three forzato)
4. Link interni — 2–4 anchor descrittivi verso prodotti o sotto-categorie
5. Chiusura — invito misurato o pattern brand
```

### Template Markdown

```markdown
## [Nome categoria]

[Definizione answer-first: «I [prodotti] in [materiale/stile] sono…»]

[Per chi conviene e in quali situazioni — esempi concreti.]

[Criterio 1 con dettaglio.] [Criterio 2 con dettaglio.]

Per approfondire: [link descrittivo 1], [link descrittivo 2].

[Chiusura brand.]
```

---

## Articolo blog

**Lunghezza:** variabile (min 400 parole per pillar)  
**Obiettivo:** informare + tenere il lettore

### Struttura

```
1. Lead — hook sensoriale o domanda concreta (no «In un mondo in cui…»)
2. Corpo — sezioni con H2, un'idea per sezione
3. Esempi — almeno 1 caso reale, dato o procedura
4. Takeaway — 2–3 frasi actionable, no «In conclusione»
```

### Template Markdown

```markdown
[Lead: 2–4 frasi. Cosa imparerà il lettore, perché ora.]

## [Sezione 1 — titolo descrittivo, non clickbait]

[Prosa con dettaglio concreto. Alterna frasi brevi e lunghe.]

## [Sezione 2]

[Esempio, procedura o confronto con dati.]

## [Cosa fare adesso]

[Takeaway actionable in prosa, non bullet generici.]
```

---

## Landing

**Lunghezza:** breve e scannable (lettore impulsivo; vedi [five-copy-blocks.md](references/five-copy-blocks.md))  
**Obiettivo:** Pain → Promise → Proof → CTA (non romanzo di vendita)

### Struttura (5 Copy Blocks — blocchi 1–3)

| Sezione | Contenuto |
|---------|-----------|
| Pre-headline | Pubblico / pain / situazione in 1 riga |
| Hero | Headline = **promise** specifica; subhead = promise + **proof** se disponibile; CTA primaria |
| Problem | 1 paragrafo **pain** concreto (linguaggio cliente) |
| Solution / bullets | Fino a **5** bullet: beneficio → vantaggio (caratteristica solo se legata a proof) |
| Social proof | Solo numeri/testimonianze/**proof** verificabili e allineati alla promise |
| CTA | Stessa azione, verbo concreto; no urgenza falsa |

### Template (landing breve)

```markdown
*[Pre-head: chi / pain]*

# [Headline — promise in chiaro, ≤~12 parole]

[Subhead: sviluppa la promise; 1 proof se vero.]

[CTA primaria — verbo concreto]

## [Pain in linguaggio del cliente]

[1 paragrafo.]

- [Beneficio 1 + proof/caratteristica → vantaggio]
- [Beneficio 2 …]
- (max 5)

[CTA finale — stessa azione]
```

**Invarianti:** una pain + una promise; **non inventare** proof; se proof assente, non riempire di claim. Dettaglio + brief campi: [five-copy-blocks.md](references/five-copy-blocks.md).

---

## Meta SEO

**Limiti:** title ≤60 caratteri, meta description ≤155 caratteri

### Pattern generico

```
Title: [Keyword primaria] + [beneficio breve] | [Brand]
Meta: [Beneficio concreto]. [Dettaglio distintivo]. [Invito soft, no stuffing].
```

### Esempio (placeholder)

```
Title: Cinturino pelle nero artigianale | [Brand]
Meta: Cinturino in vacchetta e vitello fiorentino, cucito a mano. Compatibile 18–24 mm. Spedizione [paese].
```

Controlla lunghezza caratteri prima di consegnare. Se skill SEO di progetto definisce pattern diversi → segui quello.

---

## FAQ

**Lunghezza:** ≤150 parole per risposta  
**Obiettivo:** risposta autonoma (leggibile fuori contesto, utile per schema FAQ)

### Struttura per voce

```
D: [Domanda come la farebbe un utente reale, con keyword naturale]
R: [Risposta diretta nella 1ª frase.] [Dettaglio o eccezione.] [Link interno opzionale.]
```

### Template

```markdown
### [Domanda naturale?]

[Risposta answer-first in 1 frase.] [Dettaglio verificabile.] [Se serve: vedi [pagina correlata].]
```

### Regole FAQ

- Domanda in linguaggio utente, non keyword stuffing
- Risposta autonoma: capibile senza leggere il resto della pagina
- No «Sì, assolutamente!» o filler
- Una FAQ = un tema; no domande composte

---

## Contenuto strutturato JSON-first (+ render)

**Quando:** il progetto genera Markdown (o HTML) da JSON via script; tipico newsletter, promo, carousel, schede ripetibili.

### Invarianti

1. **Fonte di verità:** file `.json` (e schema se presente)
2. **Derivati:** `.md` / `.html` prodotti solo da script di render — **non** editare a mano i derivati
3. Dopo ogni modifica al JSON: riesegui il render dichiarato dall'L2
4. Audit e rewrite sul JSON (campi body/meta); poi re-render
5. Path, nomi file, script e schema: **solo in L2** (es. `article-schema.json`, `scripts/render-*.py`)

### Workflow minimo

```
Task Progress:
- [ ] 1. Individua cartella contenuto + schema L2
- [ ] 2. Modifica / crea JSON
- [ ] 3. Valida vs schema se disponibile
- [ ] 4. Esegui script render L2
- [ ] 5. Checklist copy sul risultato; se serve fix → torna al JSON
```

### Anti-pattern

- Patch sul `.md` generato «per questa volta»
- Due fonti (JSON e MD) tenute a mano in parallelo
- Inventare path render non documentati nell'L2
