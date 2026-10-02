# Editing avanzato — solidità, taglio, profondità

Distillato da [Guida Operativa IA - Prompt Engine & Editing Avanzato.pdf](../../../GuideStile/Guida%20Operativa%20IA%20-%20Prompt%20Engine%20%26%20Editing%20Avanzato.pdf).

---

## Quando applicare

Revisione profonda, articoli lunghi, copy che «suona giusto ma non regge», humanize su testi già editati. Esegui **dopo** audit anti-AI o in parallelo se richiesto dall'utente.

**Never inject:** solidità non si ottiene inventando dati o esempi. Se mancano prove, segnala in report e chiedi source; non riempire i buchi con cifre plausibili (allinea a [anti-ai-it.md](anti-ai-it.md) § Gap-filling). Tecnica del numero: aggettivo intensificatore senza cifra nel source → **taglia** l'aggettivo.
---

## Fase 1: Controllo solidità

Agisci come editor e fact-checker. Valuta:

| Criterio | Cosa cercare |
|----------|--------------|
| Buchi logici | Conclusioni che non seguono dalle premesse |
| Mancanza di prove | Affermazioni forti senza dati, esempi, fonti |
| Bias / assunzioni | Cose date per scontate che richiedono spiegazione |
| Mondo reale | Metafore e nessi causali fisicamente plausibili |

**Output report:**

```markdown
### Solidità
- [Punti di Rottura]: errori logici o di fatto
- [Aree di Debolezza]: concetti che servono esempio/dato
- [Verdetto]: 1–10
```

| ❌ Debole | ✅ Solido |
|----------|----------|
| Le aziende che usano l'AI crescono molto più velocemente. Chi non si adegua fallirà in pochi mesi. | Il mercato sta accelerando, è vero, ma non è lineare. Secondo i report 2025, l'adozione dell'AI ha aumentato l'efficienza media del 22% nelle PMI. Chi resta indietro soffre sui margini operativi. |

---

## Fase 2: Taglio (-30% brodo)

Copywriter ossessionato da sintesi e densità informativa.

| Regola | Azione |
|--------|--------|
| **Asindeto** | Elimina connettivi ripetitivi (*tuttavia*, *inoltre*, *pertanto*, *di conseguenza*) → punto fermo |
| **Preamboli** | Rimuovi *«È importante notare che»*, *«Come abbiamo visto»*, *«In questo paragrafo esploreremo»* |
| **Nominalizzazione** | *effettuare una valutazione* → *valutare* |
| **Regola del 30%** | Riduci lunghezza del 30% mantenendo valore informativo |

**Esempio:**

- ❌ *Inoltre, è di fondamentale importanza considerare che, qualora si decidesse di implementare questa strategia, si renderebbe necessario procedere a una revisione dei costi. Tuttavia, questo ci permetterebbe di ottimizzare le risorse.*
- ✅ *Cambiare strategia richiede di rivedere i costi. È il prezzo da pagare per ottimizzare le risorse.*

---

## Fase 3: Editing stilistico profondo

Non solo refusi. Migliora qualità mantenendo voce brand.

| Filtro | Azione |
|--------|--------|
| **Criptoinglese** | *fare una discussione* → *discutere*; *condividere un pensiero* → *dire la mia* |
| **Ritmo** | Tre frasi stessa lunghezza → accorcia drasticamente la terza |
| **Uso medio** | Dislocazioni, frasi scisse; elimina rigidità scolastica |

**Esempio:**

- ❌ *Io ritengo che implementare questo tool possa fare una grande differenza per il team. Certamente, sarà necessario effettuare un training approfondito per tutti.*
- ✅ *Questo tool al team serve sul serio, può svoltare il flusso di lavoro. Certo, prima tocca mettere in conto un bel po' di formazione per tutti, altrimenti non si va da nessuna parte.*

---

## Ordine consigliato

```
Solidità (se contenuto informativo) → Taglio -30% → Anti-AI → Loop avversariale → Checklist
```

Per pattern anti-AI → [anti-ai-it.md](anti-ai-it.md).  
Per processo loop → [humanizer-loop.md](humanizer-loop.md).
