# Setswana Constituency Parser

A rule-based Natural Language Processing (NLP) system that performs **constituency parsing** on Setswana sentences. The parser identifies grammatical constituents — such as Nouns (Lerui), Verbs (Leamanyi), Pronouns (Leemedi), and Adjectives/Adverbs (Letlhaodi) — and builds a hierarchical parse tree showing the syntactic structure of each sentence.

This project was built using **Python** and the **NLTK (Natural Language Toolkit)** library, using custom Setswana linguistic resource files as its foundation. It was developed as part of an industrial attachment internship in the Department of Computer Science, University of Botswana (NLP research, supervised by Dr. G. Malema).

A key feature of this parser is that it does **not** guess a single "best" tag for ambiguous words. Instead, it generates **every possible tag sequence** for a sentence and parses each one independently, so all grammatically valid interpretations are visible at once.

---

## Project Structure

```
Constituency-Parsing/
│
├── setswana_parser.py            ← Main parser — run this to parse sentences
├── Tester.py                     ← Test suite — run this to verify the parser
├── definitions.txt               ← Setswana multi-tag word dictionary
├── Parsing_Regex.txt             ← Grammar rules for constituency parsing
```

---

## What is Constituency Parsing?

Constituency Parsing is the process of analysing a sentence and breaking it down into **groups of words that belong together**, called constituents. Each group is labelled with its grammatical role, and the result is displayed as a **parse tree**.

For example, the sentence **"kgosi reka koloi"** (the chief buys a car) is parsed as:

```
            S
    ________|________
   NP       |        NP
   |        |        |
 kgosi    reka     koloi
 (NN)    (VRB)     (NN)
```

- `kgosi` → Lerui (Noun) — forms a Noun Phrase (NP)
- `reka` → Leamanyi (Verb)
- `koloi` → Lerui (Noun) — forms another Noun Phrase (NP)

Where a word has more than one possible tag (e.g. *bone*, which can be a Verb or a Pronoun), the parser produces a **separate tree for every possible reading** of the sentence, rather than picking just one.

---

## Setswana Grammatical Categories

The parser recognises the following Setswana grammatical categories (defined in `definitions.txt`):

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
| `EE1` / `EE2` | Felo / Mokgwa | Locative / Manner | tlhoko, gaufi, thata, ruri |
| `CC1–C15` | Kgokagano | Concord / Connector | le, ba, a, se, tse |
| `L01–L62` | Karolo | Particle / Morpheme | ke, ka, ga, mme, fela |

`UNKNOWN` is used for any word not found in `definitions.txt`.

---

## Getting Started

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

### Step 2 — Set Up Your Files

Make sure all resource files are in the **same folder** as the scripts:

```
Your Project Folder
    ├── setswana_parser.py
    ├── Tester.py
    ├── definitions.txt
    └── Parsing_Regex.txt
```

### Step 3 — Run the Parser

```bash
python setswana_parser.py
```

Type any Setswana sentence at the prompt and press **Enter**. Type `exit` to quit.

---

## Example Usage

**Input:**
```
Sentence: kgosi reka koloi
```

**Output (per generated tag sequence):**
```
=====================================================================
  SENTENCE: kgosi reka koloi
=====================================================================
 WORD TAG CHECK
-----------------------------------------------------------------
  kgosi   → ['NN']        (not ambiguous)
  reka    → ['VRB']       (not ambiguous)
  koloi   → ['NN']        (not ambiguous)

 GENERATED TAG SEQUENCES: 1 sequence found
-----------------------------------------------------------------
  Sequence 1: kgosi/NN reka/VRB koloi/NN

 PARSE TREE — Bracket Notation:
-----------------------------------------------------------------
(S (NP kgosi/NN) reka/VRB (NP koloi/NN))

 PARSE TREE — Visual:
-----------------------------------------------------------------
            S
    ________|________
   NP       |        NP
   |        |        |
 kgosi    reka     koloi
```

If a word in the sentence is ambiguous (has more than one tag), multiple sequences and multiple parse trees are produced — one per possible reading. A **graphical popup window** (via `tkinter`) also opens for each generated tree.

---

## Understanding the Parse Tree

The parser produces each tree in **three formats**:

| Format | What it shows | How to use it |
|---|---|---|
| **Bracket Notation** | Compact one-line representation | Quick structure check |
| **ASCII Diagram** | Visual tree drawn in the terminal | Understand constituency groups |
| **Popup Window** | Graphical tree window (via tkinter) | Best for presentations and analysis |

To use the popup window you need **tkinter** installed:
- **Windows** — comes with Python automatically
- **Linux/Ubuntu** — run: `sudo apt-get install python3-tk`

---

## Running the Tests

To verify that the parser is working correctly, run the test suite:

```bash
python Tester.py
```

The test suite runs **7 blocks** of automated tests covering all five core functions:

| Block | What It Tests |
|---|---|
| Block 1 — `load_definitions_multi()` | Verifies the multi-tag dictionary loads correctly from `definitions.txt` |
| Block 2 — `load_grammar_rules()` | Verifies grammar rules load correctly from `Parsing_Regex.txt` |
| Block 3 — `check_word_tags()` | Verifies ambiguous vs. unambiguous words are correctly flagged |
| Block 4 — `generate_tag_sequences()` | Verifies the Cartesian product produces the correct number of sequences |
| Block 5 — `parse_sequence()` | Verifies each generated sequence produces a valid parse tree |
| Block 6 — Edge Cases | Tests unknown words, uppercase input, extra spaces |
| Block 7 — Dictionary Coverage Report | Visual summary table of all tags and word counts |

---

## Resource Files Explained

### definitions.txt

This file is the **multi-tag word dictionary** of the parser. Each line maps a grammatical tag to a list of Setswana words:

```
NN:bana.metsi.leswe.sekolo.dikoloi.koloi.tsela.
VRB:tsamaya.rata.reka.lwala.duela.goroga.
letlhaodi_thito:sentle.bonako.gantsi.thata.monate.
```

- Tags are on the **left** of the colon
- Words are on the **right**, separated by dots (`.`)
- A word can appear under more than one tag (e.g. *bone* appears under both `VRB` and `leemedi`) — `load_definitions_multi()` collects **all** of a word's tags into a list rather than keeping only the first one found.

### Parsing_Regex.txt

This file contains the **grammar rules** that tell NLTK how to group tagged words into phrases. Rules are written in NLTK's `RegexpParser` format:

```
NP: {<NN>}
    {<NP><CC6><NP>}

VP: {<VRB>}
    {<VP><NP>}
```

Each rule defines how constituents combine. For example, `{<NP><CC6><NP>}` means two Noun Phrases joined by a CC6 concord (like *le* — "and") form a larger Noun Phrase.

---

## Known Limitations

- **Dictionary size** — Words not present in `definitions.txt` are tagged as `UNKNOWN` and may not parse correctly. Adding more words improves coverage.
- **Multi-word expressions** — Phrases containing spaces (e.g. *"lwa ntlha"*, "for the first time") in the rules/definitions files are currently skipped. Single-word entries only.
- **Combinatorial growth** — Because every ambiguous word multiplies the number of generated sequences, sentences with several ambiguous words can produce a large number of parse trees, some of which may not yield structured (non-flat) trees.
- **Popup window** — The graphical tree window (`tree.draw()`) requires `tkinter`. If it is not available, the ASCII diagram is still displayed in the terminal.

---

## How to Extend the Parser

### Adding more words to the dictionary

Open `definitions.txt` and add words to the appropriate tag line using dots as separators:

```
NN:bana.metsi.sekolo.YOUR_NEW_NOUN.
VRB:tsamaya.reka.YOUR_NEW_VERB.
```

If a word can belong to more than one category, simply add it to each relevant tag line — `load_definitions_multi()` will pick up every occurrence.

### Adding new grammar rules

Open `Parsing_Regex.txt` and add rules under the appropriate constituent label:

```
NP: {<NN>}
    {<NP><CC6><NP>}
    {<YOUR_NEW_RULE>}
```

---

## Built With

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.7+ | Programming language |
| NLTK | Latest | `RegexpParser`, parse tree building and display |
| tabulate | Latest | Formatted table output in terminal |
| itertools | Built-in | `product()` for Cartesian-product tag sequence generation |
| tkinter | Built-in | Graphical parse tree popup window |
| re | Built-in | Regular expressions for parsing rule patterns |

---

## Why This Project Matters

Setswana is spoken by approximately **9 million people** across Botswana, South Africa, Zimbabwe, and Namibia. Despite this, it remains a **low-resource language** in the field of NLP — meaning there are very few computational tools built for it compared to languages like English or French.

This project contributes to bridging that gap by building an open, rule-based constituency parser specifically designed for Setswana grammar. It is part of a broader effort — alongside research communities like the **Masakhane Project** — to develop NLP technology for African languages.

---

## Changes: Week 1 → Week 2

**Week 1** focused on building the first working version of the parser:
- Implemented a dictionary-based POS tagger mapping Setswana words to grammatical tags, with each word stored under a **single** tag.
- Built the initial rule-based constituency parser using NLTK, with grammar rules loaded via regular expressions.
- Learned Python fundamentals (coming from a Java background): variables, loops, functions, classes, raw strings (`r"..."`) for Windows file paths, and `os.path` for portable, dynamic path handling.
- Produced parse tree output in bracket notation, ASCII diagrams, and `tkinter` popup windows.
- Identified a key limitation: some Setswana words (e.g. *bone*) belong to more than one grammatical category, but the single-tag dictionary could only capture one interpretation per word.

**Week 2** redesigned and rebuilt the parser around solving that limitation:
- Replaced the single-tag dictionary with **`load_definitions_multi()`**, which stores *every* tag a word can take, fully representing lexical ambiguity.
- Added **`generate_tag_sequences()`**, using `itertools.product` to generate the full Cartesian product of tag options across a sentence — so a sentence with two ambiguous words (two tags each) now produces all four valid tag sequences, instead of just one guessed sequence.
- Shifted the program's goal from *picking the single best parse* (Week 1's scoring/ranking approach) to *exposing every grammatically valid interpretation* of a sentence simultaneously — a simpler, more focused design aligned with the actual research objective.
- Rebuilt **`Tester.py`** from scratch with seven test blocks covering all five core functions, edge cases, and a dictionary coverage report.
- Verified `generate_tag_sequences()` against the example sentence from the project specification.
- Outstanding work carried into Week 3: testing against a broader range of Setswana sentences, and investigating how the grammar rules file can be extended to produce structured (non-flat) parse trees across more sentence patterns.

---

## License

This project is open source and available for academic and research use.

---
