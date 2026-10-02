# startup.registroimprese.it — access playbook

Portale: [startup.registroimprese.it](https://startup.registroimprese.it/)

Registro ufficiale (sezione speciale) di **startup innovative**, **PMI innovative**, **incubatori certificati**.

## Accesso: tre modalità (in ordine di preferenza)

### 1) File open list fornito dall’utente

Elenchi tabellari (storicamente XLS, aggiornamento settimanale riferito da MIMIT) scaricati manualmente dal portale/area open data.  
Chiedi al PO di allegare il file in `.cursor/product/data/` e analizzalo — **non inventare conteggi**.

### 2) Browser assistito

La UI può mostrare **bot/captcha**. Se il fetch HTTP automatico fallisce, guida l’utente al download o usa browser tools solo con interazione umana sul captcha. **Niente bypass.**

### 3) API vetrina InfoCamere (accreditata)

Dettaglio vetrina firmata: richiede profilo/token InfoCamere (`client_id`). Solo se L2 documenta credenziali e scopo d’uso conforme alle condizioni. Non hardcodare secret nel canone L1.

## Cosa non usare come default

- **Telemaco “Elenchi di imprese”** a pagamento per liste generiche — fuori scope open-data di questa competenza
- Scraper massivi / credential stuffing

## Analisi tipiche

- Stock e distribuzione per provincia/regione, ATECO, anno iscrizione
- Confronto startup vs PMI innovative vs incubatori (se presenti nel file)
- Caveat: definizione legale “startup innovativa” ≠ qualsiasi young company

## Citation

`Fonte: Registro Imprese / InfoCamere — elenco {startup|PMI innovative|incubatori}; file {nome}; estratto/scaricato il {YYYY-MM-DD}; portale startup.registroimprese.it`
