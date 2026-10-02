# Il Product Requirements Document

## Guida pratica per Product Owner

**A chi è rivolto questo documento**  
A chiunque nel team abbia o voglia assumere un ruolo di Product Owner, Product Manager, o sia responsabile di definire e comunicare i requisiti di un prodotto digitale. Non richiede esperienza pregressa: si parte da zero.

## Parte I — Cos'è un PRD e perché esiste

### Il problema che il PRD risolve

Immagina di dover costruire una casa senza un progetto architettonico. Ogni operaio interpreta a modo suo, il muratore parte dai muri mentre l'elettricista pensava di partire dagli impianti, e il committente scopre a metà lavoro che voleva tre finestre sul lato sud, non due. Risultato: rilavorazioni, costi extra, frustrazioni.

Nello sviluppo di prodotti digitali accade esattamente lo stesso, e più spesso di quanto si pensi.

Il **Product Requirements Document (PRD)** è quel progetto architettonico: un documento condiviso che risponde alle domande fondamentali prima che il lavoro inizi davvero.

*"Il PRD non descrive come costruire il prodotto. Descrive cosa deve fare il prodotto e perché."*

### Cosa contiene un PRD

Un PRD ben fatto risponde a queste domande in quest'ordine:

| Domanda | Sezione |
| :-- | :-- |
| Qual è il problema che stiamo risolvendo? | Vision & Contesto |
| Per chi lo stiamo risolvendo? | Personas / Utenti target |
| Cosa deve fare il prodotto, ad alto livello? | Epic Map |
| Cosa deve fare il prodotto, nel dettaglio? | User Stories |
| Come sappiamo che è fatto bene? | Criteri di accettazione + DoD |
| Cosa misuriamo per sapere se funziona? | KPIs |
| Cosa non sappiamo ancora? | Open Questions |
| Cosa abbiamo già costruito? | Artifact & Versioni |

### PRD vs altri documenti — cosa NON è un PRD

È importante chiarire cosa il PRD **non** è, perché la confusione tra questi documenti è frequente:

| Documento | Differenza dal PRD |
| :-- | :-- |
| Technical Spec | Descrive come costruire, non cosa. Il PRD precede la Technical Spec. |
| Project Plan | Descrive quando e chi fa cosa. Il PRD precede il Project Plan. |
| Backlog Jira | È la versione operativa e granulare del PRD. Il PRD è la visione d'insieme. |
| Business Case | Giustifica perché investire. Il PRD assume che la decisione sia già presa. |
| User Manual | Descrive il prodotto dopo che è stato costruito. Il PRD lo precede. |

## Parte II — Perché il PRD è importante

### 1\. Crea un linguaggio comune

In un team multidisciplinare (sviluppatori, designer, marketing, customer care, management) ogni ruolo tende a vedere il prodotto con una lente diversa. Il PRD è il documento che tutti possono leggere, capire e commentare — indipendentemente dal background tecnico.

Senza un PRD, le conversazioni tendono a girare in cerchio perché le persone stanno parlando di cose diverse usando gli stessi termini.

### 2\. Sposta le decisioni all'inizio, dove costano meno

Cambiare idea su un requisito su carta costa zero. Cambiare idea su un requisito dopo che il codice è scritto può costare giorni di rilavorazione. Dopo che il prodotto è in produzione, può costare la fiducia degli utenti.

Il PRD forza il team a confrontarsi sui requisiti *prima* di iniziare a costruire — quando le decisioni sono ancora reversibili e poco costose.

```
Costo di un cambio requisito: Documento → €1 Design → €10 Sviluppo → €100 Produzione → €1.000+
```

### 3\. Preserva la memoria del progetto

I team cambiano. Le persone cambiano ruolo, cambiano azienda, si dimenticano. Il PRD è la memoria scritta delle decisioni prese, delle ragioni dietro quelle decisioni, e delle alternative scartate.

Senza documentazione, ogni nuovo membro del team riparte da zero, ogni discussione si ripete, e ogni scelta passata diventa opaca.

### 4\. Rende il backlog prioritizzabile

È impossibile decidere cosa fare prima se non si sa *perché* esiste ogni funzionalità. Il PRD collega ogni User Story a una Epic, e ogni Epic a una parte della Vision. Questo permette al PO di rispondere alla domanda "perché questa cosa prima di quell'altra?" con argomenti concreti, non intuizioni.

### 5\. Allinea gli stakeholder prima che sia troppo tardi

Ogni stakeholder ha aspettative diverse su cosa sarà il prodotto. Il PRD le rende esplicite e richiede un'approvazione formale. Questo non elimina i disaccordi — anzi li porta in superficie — ma li porta in superficie nel momento giusto: prima dello sviluppo, non dopo.

## Parte III — Come si scrive un PRD: guida passo-passo

### Step 1 — Inizia dalla Vision, non dalle feature

L'errore più comune è iniziare a scrivere le User Stories senza prima chiarire il problema e la Vision. Il risultato è una lista di funzionalità senza filo conduttore.

**Esercizio pratico:** Prima di aprire il template, scrivi su un foglio:

1. Qual è il problema specifico che questo prodotto risolve?
2. Chi ha questo problema?
3. Cosa cambierà nella vita di questa persona grazie al nostro prodotto?
  

Solo quando riesci a rispondere in modo chiaro e conciso a queste tre domande, sei pronto a scrivere il PRD.

### Step 2 — Identifica le Personas, non i ruoli generici

"L'utente vuole..." è la frase più inutile che si possa scrivere in un PRD. Chi è "l'utente"? Ha 25 anni o 55? È esperto di tecnologia o no? Usa il prodotto ogni giorno o una volta al mese?

Le **Personas** sono descrizioni semi-fittizie di utenti reali, basate su ricerche o osservazioni dirette. Non devono essere elaborate — anche due righe bastano — ma devono essere specifiche.

**Esempio scarso:** "L'utente del Customer Care vuole trovare le informazioni velocemente."

**Esempio utile:** "Marta, 32 anni, Customer Care specialist. Gestisce 20-30 casi al giorno, spesso sotto pressione. Quando riceve una segnalazione, deve in pochi minuti capire chi è il cliente, cosa ha comprato, e cosa è andato storto — prima di rispondere o richiamare."

Le Personas non sono sempre persone fisiche. In alcuni casi il "chi" è il **sistema stesso** — un processo automatico che deve fare qualcosa senza intervento umano. In questi casi si usa la persona **"Sistema"**, e la storia descrive un comportamento automatico che ha comunque un impatto diretto sull'utente finale.

**Esempio con persona Sistema (corretto):**  
"Come **sistema**, voglio aggiornare automaticamente la lista delle recensioni negative ogni 24 ore, **così da** garantire che il team Customer Care lavori sempre su dati aggiornati senza dover avviare il processo manualmente."

Questa storia è legittima perché il beneficio — dati sempre freschi — è direttamente percepito dall'utente umano (Marta). Il sistema è il soggetto esecutore, ma l'utente è il destinatario del valore. Quando e come usare correttamente questa Persona è spiegato in dettaglio nella sezione dedicata, dopo lo Step 4.

### Step 3 — Le Epic prima delle storie

Prima di scrivere le User Stories, raggruppa le funzionalità in aree logiche — le **Epic**. Un modo utile per trovare le Epic è chiedersi: "Se questo prodotto fosse un'app, quali sarebbero le sezioni principali del menu?"

Le Epic devono essere abbastanza grandi da contenere più storie (minimo 3-5) ma abbastanza piccole da avere un tema univoco. Se un'Epic contiene storie troppo diverse tra loro, va divisa.

### Step 4 — Scrivi User Stories nel formato giusto

Il formato standard è:

**Come** \[tipo di utente specifico\],  
**voglio** \[azione o funzionalità\],  
**così da** \[beneficio concreto\].

Tre errori frequenti da evitare:

**Errore 1 — Scrivere la soluzione invece del bisogno:**

❌ "Come utente, voglio un pulsante verde in alto a destra che esporti il CSV."

✅ "Come responsabile dati, voglio esportare i dati filtrati, così da elaborarli nel mio tool preferito."

Il *come* (pulsante, posizione, colore) è decisione del designer, non del PO.

**Errore 2 — Storie troppo grandi:**

❌ "Come utente, voglio gestire il mio profilo."  
Questa storia include almeno 10 funzionalità diverse. Va spezzata.

**Errore 3 — Storie senza valore per l'utente:**

❌ "Come sistema, voglio salvare i dati nel database ogni 5 minuti."  
Questa storia è mal scritta non perché usi "sistema" come Persona — che in alcuni contesti è corretto — ma perché il beneficio non ha impatto visibile o percepibile dall'utente finale. Salvare dati nel database è un dettaglio implementativo: appartiene alla Technical Spec, non al PRD.

La versione corretta sposta il focus sul valore percepito dall'utente:

✅ "Come sistema, voglio salvare automaticamente le modifiche ogni 5 minuti, **così da** garantire che l'utente non perda il lavoro in caso di interruzione improvvisa della connessione."

La differenza è sostanziale: nella versione ✅ il "così da" descrive un beneficio concreto e visibile per chi usa il prodotto. Questo è il test da applicare sempre: *se il beneficio non tocca nessun utente reale, la storia non appartiene al PRD.*

ℹ️ Per approfondire quando è corretto usare "sistema" come Persona, vedi la sezione dedicata subito sotto.

### La Persona "Sistema" — quando e come usarla

Questa è una delle aree più fraintese nella scrittura di User Stories. Molti PO alle prime armi eliminano sistematicamente qualsiasi storia con "sistema" come Persona, convinti che sia sempre un errore. Non è così: la questione non è *chi* è il soggetto, ma *se il beneficio raggiunge un utente reale*.

#### La regola del "così da"

Il test più semplice per capire se una storia con persona Sistema appartiene al PRD è leggere il "così da" e chiedersi: **questo beneficio è percepito da qualcuno che usa il prodotto?**

| Versione | Appartiene al PRD? | Perché |
| :-- | :-- | :-- |
| "Come sistema, voglio salvare dati ogni 5 min." (senza "così da") | NO | Nessun beneficio utente esplicitato |
| "Come sistema, voglio salvare ogni 5 min, così da evitare la perdita di dati in caso di crash" | SÌ | Il beneficio (niente perdita di dati) è percepito dall'utente |
| "Come sistema, voglio indicizzare i record nel database" | NO | Dettaglio implementativo puro, va nella Technical Spec |
| "Come sistema, voglio inviare una notifica email dopo ogni nuova recensione negativa, così da allertare il team in tempo reale" | SÌ | Il beneficio (allerta tempestiva) cambia il comportamento del team |

#### Quando usare la Persona "Sistema"

La Persona "Sistema" è appropriata in tre scenari:

1. **Automazioni che sostituiscono un'azione manuale ripetitiva**  
  Il sistema fa qualcosa che altrimenti un utente dovrebbe fare a mano. Il valore è nel risparmio di tempo e nell'eliminazione dell'errore umano.
2. **Comportamenti in background con effetti visibili**  
  Il sistema esegue un processo (aggiornamento, sincronizzazione, calcolo) il cui risultato è direttamente visibile o fruibile dall'utente.
3. **Integrazioni tra sistemi con impatto sull'esperienza utente**  
  Il sistema A comunica con il sistema B, e il risultato di questa comunicazione cambia cosa vede o può fare l'utente finale.
  

#### Esempio dal progetto Trustpilot Review Tracker × HubSpot

Il nostro artifact è un caso pratico eccellente per capire la distinzione. Alcune storie erano scritte con persona umana (Marta del Customer Care), ma avrebbero potuto — o dovuto — essere scritte con persona Sistema.

**Storia attualmente nel PRD (persona umana) — corretta:**  
US-01: "Come membro del team, voglio vedere tutte le recensioni con rating inferiore a 4 stelle, **così da** avere un quadro completo del sentiment negativo."  
*Descrive il bisogno dell'utente umano di consultare i dati. È corretta e appartiene al PRD.*

**Storia che potrebbe essere aggiunta (persona Sistema) — corretta:**  
"Come **sistema**, voglio estrarre automaticamente le nuove recensioni negative da Trustpilot ogni volta che il totale aumenta rispetto all'ultimo aggiornamento, **così da** garantire che la dashboard mostri sempre i dati più recenti senza che il team debba avviare il processo manualmente."  
*Descrive l'automazione dell'aggiornamento dati — oggi fatto a mano. Appartiene al PRD perché il suo beneficio è direttamente percepito dal team.*

**Storia che NON appartiene al PRD (requisito tecnico puro):**  
❌ "Come sistema, voglio chiamare l'API di Trustpilot con header Authorization: Bearer {token} ogni 6 ore."  
*Questo è un dettaglio implementativo. Il come viene chiamata l'API appartiene alla Technical Spec, non al PRD.*

#### Schema decisionale rapido

```
Hai una storia con "Sistema" come Persona? ↓ Il "così da" descrive un beneficio percepibile dall'utente finale? ↓ SÌ → Appartiene al PRD ✅ NO → È un dettaglio implementativo → Technical Spec ❌
```

**Regola pratica:** se rimuovessi questa storia dal PRD e la mostrassi solo agli sviluppatori nella Technical Spec, gli utenti noterebbero qualcosa di diverso nel prodotto finale? Se la risposta è sì, appartiene al PRD.

### Step 5 — Criteri di accettazione: la differenza tra "fatto" e "finito"

I criteri di accettazione sono la risposta alla domanda: **"Come facciamo a sapere che questa storia è completata in modo soddisfacente?"**

Devono essere:

* **Specifici** — non "funziona bene" ma "il caricamento avviene in meno di 2 secondi"
* **Verificabili** — qualcuno deve poterli testare e dire sì/no
* **Concordati** — sia dal team di sviluppo che dallo stakeholder
  

**Esempio scarso:** "Il filtro funziona correttamente."

**Esempio utile:**  
\- Selezionando "1 stella" vengono mostrate solo le recensioni con rating = 1  
\- Il filtro si applica in meno di 500ms senza ricaricare la pagina  
\- Il filtro attivo è evidenziato visivamente con colore distinto

### Step 6 — La Definition of Done: il contratto del team

La **Definition of Done (DoD)** è diversa dai criteri di accettazione. Mentre questi ultimi sono specifici per ogni storia, la DoD è un insieme di criteri che si applicano a *tutte* le storie, sempre.

Tipicamente include:

* Il codice è stato revisionato
* I test sono stati eseguiti
* La documentazione è aggiornata
* Il PO ha approvato
  

La DoD si concorda una volta, all'inizio del progetto, e si aggiorna solo se il team decide collettivamente di cambiarla.

### Step 7 — Le Open Questions: l'onestà intellettuale del PO

Un buon PRD non pretende di avere tutte le risposte. Le **Domande Aperte** sono la sezione dove il PO ammette cosa non sa ancora e assegna a qualcuno la responsabilità di scoprirlo, con una scadenza.

Tenere traccia delle domande irrisolte è un segno di maturità. Fare finta che non esistano è il modo più sicuro per trovarsi con sorprese a metà sviluppo.

## Parte IV — Il PRD nel ciclo di vita Agile

### Come si inserisce nel processo

```
Idea ↓ [Vision + Personas] ← PO scrive la prima bozza PRD ↓ [Epic Map + User Stories] ← PO + Team, sessione di refinement ↓ [Sprint Planning] ← Team sceglie storie dalla lista prioritizzata ↓ [Sprint] ← Sviluppo ↓ [Sprint Review] ← PO verifica i criteri di accettazione ↓ [Retrospective] ← Team aggiorna la DoD se necessario ↓ [PRD aggiornato] ← PO aggiorna storie completate e backlog
```

### Il PRD è un documento vivo

Un PRD non si scrive una volta e si archivia. Va aggiornato ad ogni sprint, almeno per:

* Marcare le storie completate come Done
* Aggiungere nuove storie emerse durante lo sviluppo
* Rispondere alle Open Questions man mano che si trovano risposte
* Aggiornare le versioni degli artifact
  

Un PRD che non viene mai aggiornato dopo la prima stesura è un segnale che non viene usato davvero.

### Quanto deve essere lungo un PRD?

Non esiste una risposta universale, ma una regola utile:

* **Un PRD troppo corto** non allinea il team e lascia troppe ambiguità
* **Un PRD troppo lungo** non viene letto e quindi non allinea comunque
  

Per un progetto piccolo (2-4 settimane): 2-4 pagine, 3-6 User Stories.  
Per un progetto medio (1-3 mesi): 5-10 pagine, 10-20 User Stories organizzate in Epic.  
Per un progetto grande: più PRD, uno per Epic o area funzionale.

## Parte V — Errori da evitare

### I 7 errori più comuni dei Product Owner alle prime armi

**1\. Scrivere la soluzione invece del problema**  
Il PRD descrive *cosa* e *perché*, non *come*. Lascia il *come* al team.

**2\. Saltare la Vision e partire subito dalle storie**  
Senza Vision condivisa, ogni storia diventa un'isola disconnessa. Il team non riesce a prioritizzare perché non capisce il quadro generale.

**3\. Non coinvolgere il team nella scrittura**  
Il PRD non è un documento che il PO consegna al team. È un documento che il PO facilita e il team co-costruisce, almeno per la parte delle User Stories e dei criteri di accettazione.

**4\. Criteri di accettazione vaghi**  
"Funziona bene", "è veloce", "è intuitivo" non sono criteri — sono sensazioni. Tutto deve essere verificabile.

**5\. Non aggiornare il PRD durante lo sviluppo**  
Un PRD non aggiornato mente: mostra storie come "da fare" quando sono già completate, o non riflette i cambiamenti decisi in sprint. Diventa inutile.

**6\. Trattare il backlog come una wishlist infinita**  
Il backlog deve essere prioritizzato attivamente. Una storia che non è mai entrata in uno sprint per tre sprint consecutivi probabilmente non vale la pena di tenerla.

**7\. Confondere la completezza con la qualità**  
Un PRD con 100 storie mal scritte vale meno di uno con 10 storie precise e ben definite. Meno è meglio, se è chiaro.

## Parte VI — Checklist rapida per il PO

### Prima di iniziare a scrivere

Ho parlato con almeno un utente reale del prodotto?

So qual è il problema specifico che sto risolvendo?

Ho il buy-in degli stakeholder chiave?

### Durante la scrittura

Ogni User Story segue il formato "Come... voglio... così da..."?

Ogni storia ha almeno 2 criteri di accettazione verificabili?

Ho esplicitato cosa il prodotto NON farà?

Le domande irrisolte hanno un owner e una scadenza?

### Prima di condividere con il team

La Vision è comprensibile da chi non conosce il progetto?

Ho fatto leggere il PRD a qualcuno fuori dal team per un sanity check?

Il glossario copre tutti i termini tecnici o di dominio?

### Durante lo sprint

Il PRD riflette le decisioni prese in sprint planning?

Le storie completate sono marcate come Done?

## Risorse per approfondire

| Risorsa | Tipo | Tema |
| :-- | :-- | :-- |
| Inspired — Marty Cagan | Libro | Product Management moderno |
| The Lean Startup — Eric Ries | Libro | Validazione ipotesi prima di costruire |
| User Story Mapping — Jeff Patton | Libro | Tecniche per scrivere storie di qualità |
| Roman Pichler blog (romanpichler.com) | Blog | PRD, roadmap, OKR per PO |
| Atlassian Agile Coach (atlassian.com/agile) | Guide online | Framework Agile, Scrum, Kanban |

*Guida v1.1 — Moneysurfers ·* 20 mag 2026  
*Documento formativo interno — aggiornare in base al feedback del team*