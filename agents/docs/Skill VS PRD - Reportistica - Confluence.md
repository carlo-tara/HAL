# Skill VS PRD

**Versione:** 1.1 — **Data:** 6 ago 2026

**Autore:** @Paolo Serra

## Sintesi

**Skill** e **PRD** sono due strumenti che lavorano a livelli diversi: uno guida l'esecuzione, l'altro definisce cosa costruire.

|  | Skill | PRD |
| :-- | :-- | :-- |
| Cosa è | Istruzioni operative che l'AI esegue | Documento di specifica per un prodotto/feature |
| Chi lo "consuma" | L'AI, per sapere come fare un compito | Team umani (dev, PM, stakeholder), per sapere cosa costruire |
| Quando entra in gioco | Durante l'interazione, quando l'AI riconosce un trigger e la carica per eseguire un task | A monte, come artefatto di pianificazione/documentazione |
| Output tipico | Un'azione fatta bene (contratto generato, landing pubblicata, recap prodotto) | Un file .md con Epic, User Story, Definition of Done |
| Analogia | Una procedura operativa standard (SOP) | Un capitolato/specifica di progetto |

In una riga: **la skill insegna all'AI come lavorare, il PRD descrive cosa va costruito.** Non sono alternative, sono complementari — anzi, spesso un PRD è l'input che serve per *scrivere* una skill.

* * *

## Dettaglio

### Skill: istruzioni operative per l'AI

Una skill è un pacchetto di istruzioni (in genere un file `SKILL.md` con eventuali script/template) che definisce:

* **quando attivarsi** (i trigger — es. "contratto tra BU", "landing page")
* **come eseguire il compito** (passi, formato output, vincoli, tool da usare)
* **cosa NON fare** (limiti espliciti)
  

Esempi: `contratti-interni`, `prd-writer`, `hubspot-landing`, le skill finance (`variance-analysis`, `journal-entry`...). Ognuna codifica un know-how ripetibile: invece di spiegare ogni volta come si vuole un contratto intercompany, la regola si scrive una volta nella skill e viene eseguita consistentemente ogni volta che il contesto lo richiede.

**A cosa serve costruirle**: standardizzare processi ricorrenti, incapsulare regole di business/format specifiche dell'organizzazione, e permettere all'AI di lavorare senza dover ripetere il contesto ogni volta.

### PRD: specifica di un prodotto

Un PRD (Product Requirements Document) è un documento — non un'istruzione operativa, ma un artefatto destinato agli umani (e, di riflesso, anche all'AI quando deve costruire qualcosa a partire da esso). Descrive:

* **Contesto e vision** del prodotto/feature
* **Epic Map** con user story collegate
* **User story numerate** (US-XX) con Definition of Done
* **Backlog aperto e domande aperte**
  

La skill `prd-writer` è un esempio di come i due strumenti si intreccino: è una skill (il "come si comporta l'AI quando viene richiesto un PRD") che produce un PRD (il documento finale).

* * *

## Best practice per Product Owner: sequenza e dipendenza

La domanda giusta non è "skill o PRD", ma **in che ordine considerarli e come dipendono l'uno dall'altro**. Sequenza consigliata:

1. **PRD prima, sempre.** Prima di pensare a qualsiasi automazione, va definito *cosa* si vuole costruire: contesto, user story, Definition of Done. Il PRD è la fonte di verità sul "cosa" e sul "perché".
2. **Identificare i processi ripetibili dentro il PRD.** Una volta chiaro il prodotto, il PO individua quali user story o flussi di lavoro descritti nel PRD si ripeteranno nel tempo con logica stabile (es. "generare sempre un contratto con questa struttura", "rispondere sempre ai ticket con questo tono"). Solo questi sono candidati a diventare skill.
3. **Costruire la skill come implementazione del PRD, non in parallelo.** La skill deve derivare dalle regole già formalizzate nel PRD (Definition of Done, vincoli, formato output), non introdurne di nuove. Se durante la scrittura della skill emergono decisioni di prodotto nuove, il PO deve tornare al PRD e aggiornarlo prima di procedere: il PRD resta la fonte, la skill la conseguenza.
4. **Mantenere la dipendenza tracciabile.** Ogni skill dovrebbe poter essere ricondotta a una o più user story del PRD che la ha originata. Questo evita due errori simmetrici:
  * skill "orfane", nate da esigenze operative mai formalizzate a livello di prodotto;
  * PRD che invadono il territorio della skill descrivendo *come* eseguire un task passo-passo, invece di limitarsi al *cosa* e al *perché*.
5. **Aggiornamento ciclico, non lineare.** Quando il prodotto evolve (nuovo PRD o revisione), il PO verifica quali skill esistenti sono impattate e le aggiorna di conseguenza. La skill non vive di vita propria: segue il ciclo di vita del prodotto descritto nel PRD.
  

**Regola pratica:** se ci si accorge di scrivere regole operative dettagliate dentro un PRD, è il segnale che quella parte va estratta e trasformata in skill. Se ci si accorge che una skill richiede scelte di prodotto non ancora prese, è il segnale che va prima chiuso il PRD.

* * *

## Esercizi ed esempi reali per il team

### Esempio reale 1 — Customer care (Lorenzo)

La skill `customer-care:lorenzo-customer-care` recupera i ticket HubSpot aperti e genera bozze di risposta seguendo un prompt definito su Confluence. Questa skill non è nata dal nulla: presuppone che esista (o dovrebbe esistere) un PRD che definisce *cosa* deve garantire il processo di customer care — es. tono di voce, tempi di risposta target, casi che richiedono escalation umana. La skill implementa quelle regole; se il team cambia policy di tono o SLA, va aggiornato prima il PRD/prompt di riferimento e poi la skill che lo consuma.

### Esempio reale 2 — Contratti interni e landing HubSpot

La skill `contratti-interni` genera contratti tra Business Unit o con collaboratori esterni seguendo un template fisso; la skill `hubspot-landing` pubblica landing page a partire da script di form già validati. Entrambe sono l'implementazione operativa di decisioni già prese altrove (struttura contrattuale approvata, brand guideline della landing). Se il team lancia una nuova tipologia di collaborazione (es. un nuovo modello di fractional agreement), il primo passo non è modificare la skill: è aggiornare la logica di prodotto/business (l'equivalente del PRD) e solo dopo adattare la skill.

### Esercizio 1 — Mappare una skill esistente al suo "PRD"

Prendi una skill che il team usa già (es. `finance:journal-entry-prep` o `hubspot-landing`) e prova a scrivere, in 5 righe, quale sarebbe il PRD "implicito" che l'ha originata: qual è lo scenario d'uso, qual è la Definition of Done, quali sono i vincoli di business che la skill sta rispettando. Se non riesci a scriverlo in modo chiaro, è un segnale che la skill andrebbe documentata meglio o che il processo di business dietro non è ancora formalizzato.

### Esercizio 2 — Dal PRD alla skill

Scegli un processo ricorrente del team non ancora coperto da nessuna skill (es. la preparazione settimanale di un recap per un cliente, o una checklist di onboarding). Scrivi prima un mini-PRD (contesto, 2-3 user story, Definition of Done). Poi, a partire da quel PRD, elenca i trigger e i passi che una futura skill dovrebbe seguire per automatizzare quel processo. Questo esercizio rende esplicita la dipendenza descritta nel paragrafo di best practice: il PRD viene prima, la skill lo traduce in esecuzione.

* * *

## Storico versioni

| Versione | Data | Autore | Modifiche |
| :-- | :-- | :-- | :-- |
| 1.0 | 6 ago 2026 | @Paolo Serra | Prima stesura: sintesi, tabella comparativa, dettaglio, best practice PO |
| 1.1 | 6 ago 2026 | @Paolo Serra | Aggiunto versioning documento; aggiunto paragrafo esercizi ed esempi reali applicati al team |