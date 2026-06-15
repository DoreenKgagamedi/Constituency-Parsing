# Constituency-Parsing
# Setswana Constituency Parser

The Setswana Constituency Parser is a rule-based Natural Language Processing (NLP) system that performs constituency parsing on Setswana sentences. The parser identifies grammatical constituents — such as Nouns (Lerui), Verbs (Leamanyi), Adjectives (Lebadi), and Adverbs (Letlhaodi) — and builds hierarchical parse trees showing the syntactic structure of each sentence.

Unlike traditional parsers that select a single "best" parse, this system generates every possible tag sequence for a given sentence by respecting lexical ambiguity. When a Setswana word can belong to multiple grammatical categories (e.g., bone can be a verb OR a pronoun), the parser explores all interpretations and produces parse trees for each valid tagging.

This project was built using Python and the NLTK (Natural Language Toolkit) library, with custom Setswana linguistic resource files as its foundation.

Features

    Multi-Tag Dictionary – Every word maps to ALL its possible grammatical tags, enabling full ambiguity representation.

    Cartesian Product Sequence Generation – Uses itertools.product to generate every possible tag sequence for a sentence.

    NLTK RegexpParser Integration – Feeds each tag sequence to a grammar of Setswana constituency rules.

    Multi-Format Parse Output – For each parse tree, displays:

        Bracket notation (compact string representation)

        Visual ASCII diagram (terminal-friendly)

        Graphical popup window (via tkinter)

        Python object details

    Comprehensive Test Suite – Automated tests covering all core functions, edge cases, and coverage reporting.

    572-word Vocabulary – Covers 88 grammatical tags specific to Setswana morphosyntax.

---

##  Project Structure

```
Constituency-Parsing/
│
├── setswana_parser.py            ← Main parser — run this to parse sentences
├── Tester.py                     ← Test suite — run this to verify the parser
├── definitions.txt               ← Setswana word dictionary (572 words, 88 tags)
├── Parsing rules testing.txt     ← Grammar rules for constituency parsing
└── README.md                     ← This file
```

---

What is Constituency Parsing?

Constituency parsing breaks a sentence into groups of words that belong together, called constituents. Each group is labelled with its grammatical role, and the result is displayed as a parse tree.

For example, the sentence "Kgosi reka koloi" (The chief buys a car) is parsed as:

            S
    ________|________
   NP       |        NP
   |        |        |
 kgosi    reka     koloi
 (NN)    (VRB)     (NN)

    kgosi → Lerui (Noun) — forms a Noun Phrase (NP)

    reka → Leamanyi (Verb) — forms the Verb Phrase head

    koloi → Lerui (Noun) — forms another Noun Phrase (NP)
    
##  Setswana Grammatical Categories

The parser recognises the following Setswana grammatical categories:

| Tag | Setswana Name | English Meaning | Example Words |
|---|---|---|---|
| `NN` | Lerui | Noun | bana, kgosi, koloi, sekolo |
| `NN_ng` | Lerui (-ng) | Locative Noun | sekolong, lapeng |
| `VRB` | Leamanyi | Verb | tsamaya, reka, rata, lwala |
| `VRB_ng` | Leamanyi (-ng) | Verb -ng form | berekang, tsamayang |
| `VBPT` | Leamanyi (Past) | Past Tense Verb | ratile, buile, tsamaile |
| `VBPT_ng` | Leamanyi (-ng Past) | Past Tense -ng form | ratileng, buileng |
| `VBMD` | Leamanyi (Mood) | Mood/Subjunctive Verb | tsamaye, rate, goroge |
| `VBMD_ng` | Leamanyi (Mood -ng) | Mood Verb -ng form | tsamaeng, rateng |
| `letlhaodi_thito` | Letlhaodi | Adjective / Adverb | sentle, bonako, gantsi |
| `letlhaodi_tota` | Letlhaodi (Intensifier) | Intensifying Adverb | thata, motlhofo |
| `letlhalosi_mokgwa` | Letlhalosi Mokgwa | Manner Adverb | ruri, tota, jalo |
| `letlhalosi_nako` | Letlhalosi Nako | Time Adverb | maabane, phakela, bosigo |
| `letlhalosi_felo_P` | Letlhalosi Felo | Place Adverb | pele, morago, godimo |
| `letlhalosi_felo_D` | Letlhalosi Felo (Direction) | Directional Adverb | bokone, borwa |
| `leemedi` | Leemedi | Pronoun | rona, ena, bona, yona |
| `lesupi` | Lesupi | Demonstrative | ole, ele, yole |
| `lebadi_thito` | Lebadi | Quantifier / Number | mongwe, babedi, botlhe |
| `lesoboki` | Lesoboki | Totality Word | botlhe, otlhe, tsotlhe |
| `CC1–CC9` | Kgokagano | Concord / Connector | le, ba, a, se, tse |
| `L01–L60` | Karolo | Particle / Morpheme | ke, ka, ga, mme, fela |

---

##  Getting Started

### Prerequisites

Make sure you have **Python 3.7 or higher** installed on your computer.

Check your Python version by opening a terminal and typing:
```bash
python --version
```

### Step 1 — Install Required Libraries

Open your terminal or PowerShell and run:

```bash
pip install nltk tabulate
```

### Step 2 — Download NLTK Data

Run this once after installing NLTK:

```bash
python -c "import nltk; nltk.download('punkt')"
```

### Step 3 — Set Up Your Files

Make sure all four files are in the **same folder**:

```
 Your Project Folder
    ├── setswana_parser.py
    ├── Tester.py
    ├── definitions.txt
    └── Parsing rules testing.txt
```

### Step 4 — Run the Parser

```bash
python "setswana_parser.py"
```

You will see:

```
====================================================================
      SETSWANA CONSTITUENCY PARSER
    Multi-Tag Sequence Generator + NLTK Parser
====================================================================

 Loading definitions ...
    572 words loaded.
    X words have multiple possible tags.
 Loading grammar rules ...
    Grammar rules loaded.

Type a Setswana sentence and press Enter.
Type 'exit' to quit.

 Sentence:
```

Type any Setswana sentence and press **Enter**.

---

##  Example Usage

**Input:**
```
 Sentence: kgosi reka koloi
```

**Output:**
```
====================================================================
  SENTENCE: kgosi reka koloi
====================================================================

   WORD TAG CHECK:
--------------------------------------------------------------------
╒════╤═════════╤════════════╤═════════════╕
│  # │ Word    │ Possible Tags │ Ambiguous? │
╞════╪═════════╪═════════════╪═════════════╡
│  1 │ kgosi   │ NN          │   no        │
│  2 │ reka    │ VRB         │   no        │
│  3 │ koloi   │ NN          │   no        │
╘════╧═════════╧═════════════╧═════════════╛

   GENERATED TAG SEQUENCES (1 total):
--------------------------------------------------------------------

  Sequence 1:
    Words: kgosi reka koloi
    Tags:  NN VRB NN

   PARSE RESULTS:
====================================================================

  ── Sequence 1: NN VRB NN
--------------------------------------------------------------------
  a) Bracket Notation:
     (S (NP kgosi/NN) reka/VRB (NP koloi/NN))

  b) Visual Tree (ASCII):
            S
    ________|________
   NP       |        NP
   |        |        |
 kgosi    reka     koloi

  c) Python Object Representation:
     Type : <class 'nltk.tree.Tree'>
     Label: S
     Leaves (words): ['kgosi', 'reka', 'koloi']
     Structured: Yes

  Phrases identified:
  Phrase    Words          Tags
  -------   -------------  ----------
  NP        kgosi          NN
  NP        koloi          NN
```

A **graphical popup window** also opens showing the full tree diagram.

---

##  Understanding the Parse Tree

The parser produces the tree in **three formats**:

| Format | What it shows | How to use it |
|---|---|---|
| **Bracket Notation** | Compact one-line representation | Quick structure check |
| **ASCII Diagram** | Visual tree drawn in the terminal | Understand constituency groups |
| **Popup Window** | Graphical tree window (via tkinter) | Best for presentations and analysis |

To use the popup window you need **tkinter** installed:
- **Windows** — comes with Python automatically
- **Linux/Ubuntu** — run: `sudo apt-get install python3-tk`

---

##  Running the Tests

To verify that the parser is working correctly, run the test suite:

```bash
python Tester.py
```

The test suite runs **6 blocks** of automated tests:

| Block | What It Tests |
|---|---|
| Block 1 — File Loading | Verifies both resource files load correctly |
| Block 2 — Word Tagging | Tests 19 individual words across all POS categories |
| Block 3 — Sentence Tagging | Tests 9 complete Setswana sentences |
| Block 4 — Parse Tree Structure | Verifies NP chunks and tree structure |
| Block 5 — Edge Cases | Tests unknown words, uppercase input, extra spaces |
| Block 6 — Coverage Report | Visual table of all tags and word counts |

A passing run looks like this:

```
============================================================
   📊 TEST RESULTS SUMMARY
============================================================
╒══════════════════╤═════════╤══════════╕
│ Result           │  Count  │ Rate     │
╞══════════════════╪═════════╪══════════╡
│  Tests Passed    │   58    │ 100.0%   │
│  Tests Failed    │    0    │          │
│  Warnings        │    0    │          │
│  Total Tests     │   58    │          │
╘══════════════════╧═════════╧══════════╛

ALL TESTS PASSED! Your parser is working perfectly!
```

---

##  Resource Files Explained

### definitions.txt

This file is the **word dictionary** of the parser. Each line maps a grammatical tag to a list of Setswana words:

```
NN:bana.metsi.leswe.sekolo.dikoloi.koloi.tsela.
VRB:tsamaya.rata.reka.lwala.duela.goroga.
letlhaodi_thito:sentle.bonako.gantsi.thata.monate.
```

- Tags are on the **left** of the colon
- Words are on the **right**, separated by dots (`.`)
- The file currently contains **572 words** across **88 grammatical tags**

### Parsing rules testing.txt

This file contains the **grammar rules** that tell NLTK how to group tagged words into phrases. Rules are written in NLTK's RegexpParser format:

```
NP: {<NN>}
    {<NP><CC6><NP>}

VP: {<VRB>}
    {<VP><NP>}
```

Each rule defines how constituents combine. For example, `{<NP><CC6><NP>}` means two Noun Phrases joined by a CC6 concord (like *le* — "and") form a larger Noun Phrase.

---

##  Known Limitations

- **Dictionary size** — The parser currently knows 572 words. Words not in `definitions.txt` are tagged as `UNKNOWN` and may not parse correctly. Adding more words to the definitions file will improve results.
- **Ambiguous words** — Some Setswana words appear in multiple grammatical categories. The parser assigns the tag from whichever category lists the word first in `definitions.txt`. Examples: *tsamaeng* (tagged `VBMD_ng`), *ruri* (tagged `letlhaodi_thito`).
- **Multi-word expressions** — Phrases like *"lwa ntlha"* (for the first time) in the rules file are currently skipped. Single-word entries only.
- **Popup window** — The graphical tree window (`tree.draw()`) requires `tkinter`. If it is not available, the ASCII diagram is still displayed in the terminal.

---

##  How to Extend the Parser

### Adding more words to the dictionary

Open `definitions.txt` and add words to the appropriate tag line using dots as separators:

```
NN:bana.metsi.sekolo.YOUR_NEW_NOUN.
VRB:tsamaya.reka.YOUR_NEW_VERB.
```

### Adding new grammar rules

Open `Parsing rules testing.txt` and add rules under the appropriate constituent label:

```
NP: {<NN>}
    {<NP><CC6><NP>}
    {<YOUR_NEW_RULE>}
```

---

##  Built With

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.7+ | Programming language |
| NLTK | Latest | RegexpParser, parse tree building and display |
| tabulate | Latest | Formatted table output in terminal |
| tkinter | Built-in | Graphical parse tree popup window |
| re | Built-in | Regular expressions for parsing rule patterns |

---

##  Why This Project Matters

Setswana is spoken by approximately **9 million people** across Botswana, South Africa, Zimbabwe, and Namibia. Despite this, it remains a **low-resource language** in the field of NLP — meaning there are very few computational tools built for it compared to languages like English or French.

This project contributes to bridging that gap by building an open, rule-based constituency parser specifically designed for Setswana grammar. It is part of a broader effort — alongside research communities like the **Masakhane Project** — to develop NLP technology for African languages.

---

##  License

This project is open source and available for academic and research use.

---

*Built with for the Setswana language and African NLP research.*
