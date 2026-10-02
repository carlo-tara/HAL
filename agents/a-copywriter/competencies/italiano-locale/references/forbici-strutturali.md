# Forbici strutturali — densità sintattica italiana

Target di densità (% di frasi che contengono ciascuna peculiarità) per copy web lungo. Derivati da un corpus di prosa letteraria contemporanea, non da «grammatica ideale».

Definizioni delle peculiarità: [costruzioni-frase-italiano.md](../../../GuideStile/costruzioni-frase-italiano.md).  
Analisi numerica: [analisi-peculiarita.md](../../../GuideStile/PremioStrega/analisi-peculiarita.md).

---

## Origine corpus

| Elemento | Dettaglio |
|----------|-----------|
| Fonti | 5 romanzi vincitori Premio Strega (PDF in `GuideStile/PremioStrega/`) |
| Naming asset | Solo titolo del libro, spazi → trattini (`Come-daria.pdf`); niente autore, editore o tag z-library |
| Perimetro | Capitoli narrativi + Prologo/Epilogo; esclusi frontespizio, indice, ringraziamenti, note |
| Metodo forbice | Trim min+max sui 5 libri = 3 valori centrali (forbice **minima/onesta**). Dove un outlier distorceva il bordo, esclusione esplicita (vedi note in tabella) |
| Unità | % frasi che matchano la peculiarità (una frase può matchare più tratti) |
| Aggiornare numeri | `python3 GuideStile/PremioStrega/analyze_peculiarita.py` (spaCy `it_core_news_md`) → riscrive `analisi-peculiarita.md`; poi ricalcola trim e aggiorna la tabella forbici qui |

Obiettivo: testi generati da a-copywriter che **rispettino più o meno** queste densità, non una replica stilistica dei romanzi.

Dettaglio cartella corpus: [PremioStrega/README.md](../../../GuideStile/PremioStrega/README.md).

---

## Tabella forbici (obbligatorie)

| Peculiarità | Forbice target (% frasi) | Note |
|-------------|--------------------------|------|
| Pro-drop (soggetto nullo) | **48–59%** | mediana ~53% |
| Sistema clitico preverbale | **43–45%** | già strettissima |
| Partitivo *ne* | **1.8–3.1%** | fenomeno raro |
| Costruzioni con *si* | **12–16%** | trim; Mari outlier escluso dal bordo alto |
| Congiuntivo in subordinate | **7–15%** | trim; evita schiacciare a 0% (Di Pietrantonio basso) |
| Dislocazione topic/focus | **3.8–4.4%** | forbice più stretta del corpus grezzo |
| Ausiliare essere/avere (composti) | **25–36%** | |
| Clitic climbing | **1.1–2.1%** | raro; non forzare |

---

## Quando applicare

| Contesto | Modalità |
|----------|----------|
| Blog, landing body, email narrative, case study, pezzi lunghi (~**≥40–50 frasi**) | **Rigorosa**: stima euristica post-draft; correggi se un tratto è assente o gonfiato |
| Meta, FAQ, microcopy, titoli, CTA, pezzi corti | **Orientamento qualitativo**: usa i tratti (pro-drop, clitici, *si*…), **non** contare percentuali |

Non serve rilanciare spaCy in produzione: basta l'autoverifica euristica sotto.

---

## Per peculiarità — esempi copy web

### Pro-drop (48–59%)

| | Esempio |
|---|--------|
| Dentro | *Apri il pannello, scegli il piano, conferma. In pochi minuti sei operativo.* |
| Fuori (calco EN / LLM) | *Tu apri il pannello. Tu scegli il piano. Tu confermi. Tu sei operativo in pochi minuti.* |

### Sistema clitico preverbale (43–45%)

| | Esempio |
|---|--------|
| Dentro | *Te lo mostriamo in demo. Se ti serve, te lo attiviamo lo stesso giorno.* |
| Fuori | *Mostriamo a te la demo. Se serve a te, attiviamo per te lo stesso giorno.* |

### Partitivo *ne* (1.8–3.1%)

| | Esempio |
|---|--------|
| Dentro | *Ne abbiamo tre varianti. Se ne vuoi una di prova, scrivici.* |
| Fuori | *Abbiamo tre varianti di esse. Se vuoi una di esse di prova…* (oppure zero *ne* in un pezzo lungo dove cadrebbe naturale) |

Fenomeno raro: 1–2 occorrenze in un articolo bastano; non spargerlo a forza.

### Costruzioni con *si* (12–16%)

| | Esempio |
|---|--------|
| Dentro | *Si configura in pochi click. Si evita così il lavoro manuale sul foglio.* |
| Fuori | *Viene configurato in pochi click. Il lavoro manuale sul foglio viene evitato.* (passivo EN a catena, senza *si*) |

### Congiuntivo in subordinate (7–15%)

| | Esempio |
|---|--------|
| Dentro | *È importante che il team sia allineato prima del go-live.* |
| Fuori | *È importante che il team è allineato…* / pezzo lungo senza alcun congiuntivo dove il dubbio/volere lo richiederebbe |

### Dislocazione topic/focus (3.8–4.4%)

| | Esempio |
|---|--------|
| Dentro | *Il report mensile, lo ricevi ogni primo del mese.* |
| Fuori | Solo SVO piatto tipo *Ricevi il report mensile ogni primo del mese.* in un testo lungo senza mai ripresa clitica |

Poche dislocazioni bastano; non abusare (forbice stretta).

### Ausiliare essere/avere nei composti (25–36%)

| | Esempio |
|---|--------|
| Dentro | *Siamo partiti a marzo. Abbiamo chiuso il primo ciclo a giugno.* |
| Fuori | Solo *avere* ovunque (*Abbiamo partito…*) o solo *essere* su transitivi |

### Clitic climbing (1.1–2.1%)

| | Esempio |
|---|--------|
| Dentro | *Lo puoi attivare da subito.* (accanto a *Puoi attivarlo…*) |
| Fuori | Forzare climbing in ogni frase con verbo ristrutturante |

Raro: ammetti entrambe le forme; non inseguire la forbice.

---

## Checklist autoverifica post-draft (euristica)

Su pezzi lunghi (~≥40–50 frasi), rileggi e segna a occhio:

1. **Pro-drop** — circa metà delle frasi omette il soggetto pronominale? Se ogni frase apre con *Io/Tu/Noi/Voi/Loro*, abbassa i pronomi.
2. **Clitici** — *lo/la/li/le/mi/ti/ci/vi/gli/le* preverbali presenti a densità alta (quasi una frase su due)? Se i complementi sono sempre NP pieni (*a te*, *il prodotto*), riprendi con clitico.
3. ***ne*** — almeno un paio di *ne* naturali se parli di quantità/parte? Se zero e il tema lo consente, aggiungine uno.
4. ***si*** — impersonale/passivante/medio a tratti (una frase su 6–8 circa)? Evita solo passivi *viene/è stato* a catena.
5. **Congiuntivo** — qualche subordinate con *che* + congiuntivo (volere, necessità, dubbio)? Non azzerarlo.
6. **Dislocazione** — 1–2 riprese topic/focus con clitico nel pezzo? Non di più del necessario.
7. **Essere/avere** — mix sensato nei tempi composti (unaccusativi vs transitivi)?
8. **Climbing** — opzionale; se compare 0–1 volta in un articolo lungo, va bene.

Su meta/FAQ/microcopy: verifica solo che i tratti usati suonino italiani (clitici, pro-drop, *si*), senza conteggio.

---

## Cosa non fare

- Non forzare *ne* o climbing per «centrare la %»
- Non imitare stile letterario Strega (lessico, ritmo narrativo) — solo densità dei tratti strutturali
- Non applicare conteggi percentuali a stringhe sotto ~40 frasi
