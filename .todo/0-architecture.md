What follows below the equal signs is a first draft of an architectural specification made by another agent. We will be reviewing this together and staging it. We're not going to do this all at once, and we might not even do it all exactly this way. 

# ====

# **ARCHITECTURAL SPECIFICATION: Wikipedia Phonetic Pronunciation Extractor & Compiler (v2)**

## **1\. System Overview & Objectives**

This pipeline extracts phonetic pronunciations (via human-curated {{IPAc-en}} and {{respell}} templates) from English Wikipedia, targeting low-compute, memory-constrained mobile environments (e.g., an offline, F-Droid-compliant Android TTS Wikipedia reader).  
Instead of random sampling, this system uses a deterministic, top-down discovery strategy. It cross-references Wikipedia's pronunciation templates against:

> 1. **Wikipedia's Vital Articles Hierarchy** (Canonical cultural knowledge)  
> 2. **Wikimedia REST API Top Pageviews** (Empirical popularity)

The system generates an indexed, read-optimized **SQLite database** using WITHOUT ROWID tables and a compressed **TSV artifact** (.tsv.gz).  
The system runs in two modes:

> * **Local CLI Mode:** Executed locally by developers, fetching article hierarchies and wikitext via the public MediaWiki Action and REST APIs.  
> * **Toolforge Worker Mode:** Executed as a scheduled Kubernetes batch job on Wikimedia Toolforge, using direct read replicas where applicable.

## **2\. User Configuration Schema (Top-Level Configuration)**

All configurable parameters are isolated in a top-level configuration module (config.yaml). The parameters control exactly how "deep" into the vital and popular hierarchies the system searches.  
\# config.yaml \- User Extraction and Pruning Configuration

pipeline:  
  \# Mode of discovery: 'toolforge' (MariaDB replica) or 'api' (MediaWiki public APIs)  
  execution\_mode: "api"  
  log\_level: "INFO"

hierarchy\_depth:  
  \# VITAL ARTICLES CONFIGURATION  
  \# How deep into the Vital Articles hierarchy to ingest (1 through 5).  
  \# e.g., Level 4 covers \~10,000 articles. Set to 0 to disable Vital Articles.  
  vital\_articles\_level: 4

  \# TRENDING / POPULARITY CONFIGURATION  
  \# The number of most-viewed articles to evaluate from the pageviews API.  
  \# For local testing, set this to 1\. For production, 5000 \- 10000\.  
  popular\_articles\_limit: 1000

  \# Time range for popularity: 'last-month' or 'last-year'  
  popularity\_timeframe: "last-month"

  \# Minimum absolute monthly pageviews required for a popular article to be retained.  
  \# Filters out false-positive anomalies (e.g., bot spikes).  
  min\_monthly\_pageviews: 500

extraction\_tuning:  
  \# Number of pages to request concurrently in section 0 wikitext fetching  
  api\_chunk\_size: 50  

  \# Polite delay between batch requests (seconds)  
  api\_rate\_limit\_delay: 0.1  

  \# Custom HTTP User-Agent header (required by Wikimedia API policy)  
  user\_agent: "WikiPronunciationExtractor/2.0 (contact@example.com)"

storage\_and\_export:  
  sqlite\_output\_path: "dist/pronunciations.sqlite"  
  tsv\_output\_path: "dist/pronunciations.tsv.gz"  

  \# Options: 'both', 'respell' (plain text English), 'ipa' (IPA symbols)  
  output\_format: "both"

  sqlite\_pragma:  
    journal\_mode: "OFF"  
    page\_size: 4096  
    synchronous: "OFF"  
    cache\_size: \-2000     \# 2 MB RAM limit  
    temp\_store: "MEMORY"

normalization\_rules:  
  strip\_disambiguation\_parentheses: true  
  keep\_multiword\_entities: true  
  \# Excludes Special, User, Category, and Talk namespaces from popularity results  
  exclude\_non\_article\_namespaces: true

## **3\. Architecture & Module Decomposition**

wikipron-extractor/  
├── config.yaml  
├── requirements.txt  
├── toolforge\_job.sh  
├── wikidict/  
│   ├── \_\_init\_\_.py  
│   ├── cli.py                      \# CLI entrypoint  
│   ├── config.py  
│   ├── discovery/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── popular.py              \# Wikimedia REST API Top Views client  
│   │   ├── vital.py                \# Vital articles category extraction  
│   │   └── intersection.py         \# Merges and deduplicates discovery lists  
│   ├── extraction/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── fetcher.py              \# Batch lead section wikitext fetcher  
│   │   ├── parser.py               \# mwparserfromhell template parser  
│   │   └── diaphonemes.py          \# IPAc-en to canonical IPA/Respell map  
│   └── storage/  
│       ├── \_\_init\_\_.py  
│       ├── sqlite\_writer.py        \# Optimized SQLite compiler  
│       └── tsv\_writer.py  
└── tests/  
    ├── test\_parser.py  
    └── test\_sqlite\_writer.py

### **Module Responsibilities**

#### **wikidict.discovery**

> * **popular.py:** Fetches the top viewed articles using the Wikimedia REST API.  

* *Endpoint:* https\://wikimedia.org/api/rest\_v1/metrics/pageviews/top/en.wikipedia/all-access/yyyy/mm/all-days  
* Automatically resolves the date string based on the popularity\_timeframe configuration (e.g., if "last-month", calculates the previous calendar month).  
* Filters out known false positives: Main\_Page, Search, and any title containing Special:, Wikipedia:, or File:.  
* Returns the top N titles up to popular\_articles\_limit.  
  
  > * **vital.py:** Fetches the canonical list of Vital Articles.  
* *Method:* In api mode, queries the Action API for category members of Category:All\_Wikipedia\_level\_X\_vital\_articles. In toolforge mode, queries the categorylinks table in MariaDB.  
  
  > * **intersection.py:** Combines the lists from popular.py and vital.py. Deduplicates titles to ensure a single unique set of candidate articles before passing them to the wikitext fetcher.

#### **wikidict.extraction**

> * **fetcher.py:** Takes the candidate list, batches it into groups of api\_chunk\_size, and queries the MediaWiki Action API for rvsection=0 (the lead section).  
> * **parser.py:** Uses mwparserfromhell to parse the returned wikitext.  

* If a candidate article *does not* contain {{IPAc-en}} or {{respell}}, it is discarded (since it does not have a human-curated pronunciation trap).  
* If the template exists, extracts the diaphonemes or respell syllables.  
  
  > * **diaphonemes.py:** Translates raw Wikipedia diaphonemes into canonical IPA. If output\_format is set to "respell", mathematically maps IPA diaphonemes to plain-English respelling syllables according to Wikipedia's Help:Pronunciation respelling key.

#### **wikidict.storage**

> * **SQLite Compiler:** Compiles the parsed outputs into the pronunciations table enforcing WITHOUT ROWID.

## **4\. Execution Workflows & CLI Interface**

The CLI allows for deep overriding of the YAML configuration, which is especially useful for rapid deterministic testing.

### **Local Deterministic Testing**

To test the pipeline against just the absolute \#1 most popular article and the \#1 Vital Article without waiting for a full build:  
python \-m wikidict.cli \\  
  \--mode api \\  
  \--vital-level 1 \\  
  \--popular-limit 1 \\  
  \--sqlite dist/test\_pronunc.db

### **Full Production Build (Local)**

To execute a build combining Level 4 Vital Articles (\~10k articles) and the top 5,000 trending topics:  
python \-m wikidict.cli \\  
  \--mode api \\  
  \--vital-level 4 \\  
  \--popular-limit 5000 \\  
  \--popularity-timeframe last-month \\  
  \--sqlite dist/production\_pronunc.db

### **Toolforge Deployment**

\# Clone the repository  
git clone \<your-repo-url\> app  
cd app  
python3 \-m venv venv  
source venv/bin/activate  
pip install \-r requirements.txt

\# Execute production job  
toolforge jobs run wikidict-updater \\  
  \--command "\$HOME/app/toolforge\_job.sh" \\  
  \--image python3.11 \\  
  \--schedule "@weekly"  
