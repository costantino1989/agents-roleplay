Perfetto. Di seguito trovi **una documentazione strutturata e chiara**, pensata **per un code agent**, scritta in modo
prescrittivo (cosa fare, come farlo, con quali strumenti), così che possa implementare correttamente la simulazione
usando **LangGraph**.

Ho usato **Markdown**, sezioni chiare, enumerazioni, e indicazioni operative esplicite.

---

# 📘 Documentazione – Simulazione HR Onboarding con LangGraph

## 1. Obiettivo del sistema

L’obiettivo è creare **una simulazione autonoma (role-play)** tra:

* 🧑‍💼 **HR** di un’azienda di consulenza chiamata **Pizzagalli&Co**
* 🧑‍💻 **Nuovo assunto**

Lo scopo dell’HR è **costruire un profilo (“impronta”) del nuovo assunto** attraverso una serie di domande mirate, così
da facilitarne l’integrazione e il benessere fin dall’inizio.

La simulazione:

* non prevede input umani dopo l’avvio
* termina quando tutte le informazioni rilevanti sono state raccolte
* termina con un saluto finale da parte del nuovo assunto

---

## 2. Informazioni da raccogliere (Schema dati)

L’HR deve raccogliere progressivamente informazioni che popolano la seguente struttura:

```json
{
  "digital_behavior": {},         
  "work_values": {},              
  "learning_development": {},     
  "diversity_inclusion": {},      
  "civic_engagement": {},         
  "communication_preferences": {}
}
```

### Descrizione dei campi

* **digital_behavior**: uso di internet, device preferiti, comfort digitale
* **work_values**: flessibilità, autonomia, work-life balance
* **learning_development**: stile di apprendimento, upskilling, coaching
* **diversity_inclusion**: sensibilità a LGBTQ+, multiculturalità, inclusione
* **civic_engagement**: attivismo, cause sociali, sostenibilità
* **communication_preferences**: canali preferiti, meeting, feedback

L’HR **non è obbligato a compilare tutto subito**, ma deve assicurarsi che **tutti i campi siano coperti prima della
chiusura** della conversazione.

---

## 3. Flusso iniziale (Pre-processing utente)

All’avvio della simulazione, il sistema deve inizializzare il profilo del nuovo assunto chiedendo o impostando:

* `name`
* `age`
* `country`

### Determinazione della generazione

```python
if 18 <= age <= 29:
    generation = "genz"
else:
    generation = "millenials"
```

Queste variabili:

* `generation` ∈ {`genz`, `millenials`}
* `country` (stringa)

👉 **Devono essere salvate nello state di LangGraph**
👉 **Devono essere usate come filtri per il RAG (ChromaDB)**

---

## 4. Architettura generale con LangGraph

Il sistema deve essere implementato usando **LangGraph** con:

* **2 agenti autonomi**
* **1 stato condiviso**
* **2 tool disponibili per l’HR**
* **loop di conversazione fino a completion**

### Stato globale (esempio concettuale)

```python
state = {
  "generation": "genz" | "millenials",
  "country": "Italy",
  "profile": {...},              # struttura dati del nuovo assunto
  "conversation_history": [],
  "completed_sections": []
}
```

---

## 5. Agenti

### 5.1 HR Agent (Pizzagalli&Co)

**Ruolo:** HR di una società di consulenza
**Azienda:** Pizzagalli&Co

Il code agent deve:

* assegnare **nome**
* assegnare **sesso**
* definire una **personalità coerente con il ruolo HR**
* definire obiettivi chiari

#### Obiettivi dell’HR

* Accogliere il nuovo assunto
* Metterlo a suo agio
* Porre domande in modo empatico e progressivo
* Usare il RAG per decidere **quale tema affrontare per primo**
* Salvare informazioni rilevanti quando necessario
* Terminare la conversazione solo quando il profilo è completo

#### Comportamento richiesto

* L’HR **deve sempre decidere se una risposta è rilevante**
* Se rilevante → chiama il tool di salvataggio
* Può chiamare **RAG e salvataggio in parallelo**
* Non deve fare domande casuali: ogni domanda deve avere uno scopo

---

### 5.2 Nuovo Assunto Agent

**Ruolo:** nuovo dipendente
**Età:** millennial (fissa)
**Background:** inventato dal code agent

Il code agent deve:

* assegnare **nome**
* assegnare **sesso**
* creare una **storia personale e professionale**
* definire obiettivi (ambientarsi, capire l’azienda, sentirsi accolto)

#### Comportamento richiesto

* Rispondere in modo coerente alla propria storia
* Non conoscere il meccanismo della simulazione
* Salutare e chiudere la conversazione quando l’HR conclude

---

## 6. Tool disponibili per l’HR

### 6.1 Tool RAG (Vector Store – ChromaDB)

**Nome:** `rag`

#### Input

```json
{
  "generation": "genz" | "millenials",
  "country": "string",
  "query": "string"
}
```

* `generation`: ENUM obbligatorio
* `country`: paese del nuovo assunto
* `query`: frase che descrive il tipo di informazione cercata
  (es. “work values for gen z employees”)

#### Output

* Stringa contenente **tutti i documenti rilevanti concatenati**
* Il formato deve essere compatibile con LangGraph tool return

👉 Serve all’HR per:

* decidere **quale tema è prioritario**
* formulare la **prossima domanda**

---

### 6.2 Tool di salvataggio informazioni

**Nome:** `save_employee_info`

#### Input

```json
{
  "info": "string"
}
```

* `info` contiene **l’informazione completa da salvare**
* Il tool deve salvare i dati in un **file Markdown**

#### Comportamento

* Può essere chiamato più volte
* Il file Markdown cresce progressivamente
* Il formato è libero ma deve essere leggibile (titoli, bullet, sezioni)

---

## 7. Logica conversazionale

1. HR:

    * dà il benvenuto
    * usa il RAG per decidere **la prima domanda**
2. Nuovo assunto risponde
3. HR:

    * valuta la risposta
    * se rilevante → salva
    * decide il prossimo tema (RAG opzionale)
4. Loop fino a quando:

    * tutte le sezioni del profilo sono coperte
5. HR conclude
6. Nuovo assunto saluta
7. Simulazione termina

---

## 8. Requisiti chiave

* ✅ Simulazione completamente autonoma
* ✅ Uso obbligatorio di LangGraph
* ✅ Due agenti distinti con prompt dedicati
* ✅ Uso reale dei tool (non fittizio)
* ✅ File Markdown come output finale del profilo
* ✅ Conversazione naturale, non meccanica

---

## 9. Libertà del code agent

Il code agent **può**:

* migliorare gli obiettivi degli agenti
* arricchire i prompt
* rendere l’HR più empatico o strategico
* aggiungere logica di priorità tra le sezioni

A patto che:

* **l’obiettivo principale rimanga invariato**
* **tutti i dati vengano raccolti**

---

Se vuoi, nel prossimo messaggio posso:

* ✍️ scrivere **i prompt completi dei due agenti**
* 🧠 progettare **lo state machine LangGraph**
* 🧩 fornire **uno skeleton di codice** pronto da implementare
