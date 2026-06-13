"""
============================================================
  SETSWANA CONSTITUENCY PARSER
  Uses: definitions.txt + Parsing Regex.txt
  Library: NLTK RegexpParser

  CORE WORKFLOW:
  ──────────────────────────────────────────────────────────
  1. Load definitions.txt → build multi-tag dictionary
     (every word maps to ALL its possible tags)

  2. Take a sentence from terminal input

  3. Check each word for multiple tags

  4. Generate every possible tag-sequence combination
     for the sentence (one per ambiguous word permutation)

  5. Feed each generated tag sequence to NLTK RegexpParser

  6. For each sequence: output the tag sequence, parse tree
     in text form, bracket notation, and visual diagram
============================================================
"""

import re
import os
import nltk
from itertools import product
from tabulate import tabulate


# ──────────────────────────────────────────────────────────
# LABEL MAP
# Human-readable names for every tag code
# ──────────────────────────────────────────────────────────

LABEL_MAP = {
    'VRB':               'Leamanyi (Verb)',
    'VRB_ng':            'Leamanyi_ng (Verb -ng form)',
    'VBMD':              'Leamanyi (Mood Verb)',
    'VBMD_ng':           'Leamanyi_ng (Mood Verb -ng)',
    'VBPT':              'Leamanyi (Past Tense Verb)',
    'VBPT_ng':           'Leamanyi_ng (Past Verb -ng)',
    'NN':                'Lerui (Noun)',
    'NN_ng':             'Lerui_ng (Noun -ng form)',
    'letlhaodi_thito':   'Letlhaodi (Adjective/Adverb)',
    'letlhaodi_tota':    'Letlhaodi_tota (Intensifier)',
    'letlhalosi_felo_P': 'Letlhalosi Felo (Place Adverb)',
    'letlhalosi_felo_D': 'Letlhalosi Felo (Direction)',
    'letlhalosi_felo':   'Letlhalosi Felo (Distance)',
    'letlhalosi_mokgwa': 'Letlhalosi Mokgwa (Manner Adverb)',
    'letlhalosi_nako':   'Letlhalosi Nako (Time Adverb)',
    'lesupi':            'Lesupi (Demonstrative)',
    'lebadi_thito':      'Lebadi (Quantifier/Number)',
    'leemedi':           'Leemedi (Pronoun)',
    'lesoboki':          'Lesoboki (Totality Word)',
    'EE1':               'Felo (Locative)',
    'EE2':               'Mokgwa (Manner)',
    'UNKNOWN':           'Ga go itsege (Unknown)',
}
for _i in range(1, 16):
    _key = f'CC{_i}' if _i <= 9 else f'C{_i}'
    LABEL_MAP[_key] = f'Kgokagano {_key} (Concord/Connector)'
for _i in range(1, 63):
    LABEL_MAP[f'L{_i:02d}'] = f'Karolo L{_i:02d} (Particle/Morpheme)'


# ──────────────────────────────────────────────────────────
# FUNCTION 1: load_definitions_multi()
#
# PURPOSE: Load every word from definitions.txt and map
#          each word to ALL its possible tags.
#
# WHY: A word like "bone" appears under both VRB and leemedi
#      in definitions.txt. A plain dictionary would only
#      store one. This function stores ALL of them so the
#      parser can consider every possibility.
#
# RETURNS: { 'word': ['TAG1', 'TAG2', ...], ... }
#          Single-tag words still get a one-item list.
# ──────────────────────────────────────────────────────────

def load_definitions_multi(filepath):
    """
    Reads definitions.txt and builds a multi-tag dictionary.

    Each line in definitions.txt looks like:
        TAG:word1.word2.word3.

    This function collects ALL tags for every word so that
    ambiguous words (words appearing under multiple tags)
    are fully represented.
    """
    word_to_tags = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and lines without a colon
            if not line or ':' not in line:
                continue

            # Skip the inline grammar rule at the bottom of definitions.txt
            if line.startswith('letlhaodi:') and '{' in line:
                continue

            # Split on first colon only → TAG and word list
            parts     = line.split(':', 1)
            tag       = parts[0].strip()
            words_str = parts[1].strip().replace(',', '.')
            words     = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                # Skip multi-word expressions for now
                if ' ' in word:
                    continue
                # Initialise list if first time seeing this word
                if word not in word_to_tags:
                    word_to_tags[word] = []
                # Add tag only if not already stored for this word
                if tag not in word_to_tags[word]:
                    word_to_tags[word].append(tag)

    return word_to_tags


# ──────────────────────────────────────────────────────────
# FUNCTION 2: load_grammar_rules()
#
# PURPOSE: Read Parsing Regex.txt and produce a formatted
#          grammar string for NLTK RegexpParser.
#
# RETURNS: A single string in NLTK grammar format, e.g.:
#          NP: {<NN>}
#            | {<NP><CC6><NP>}
#          VP: {<VP><NP>}
# ──────────────────────────────────────────────────────────

def load_grammar_rules(filepath):
    """
    Reads the grammar rules file and builds the grammar
    string that NLTK RegexpParser needs to parse sentences.
    """
    rules       = {}
    current_tag = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if not line.strip():
                continue
            if line.strip().startswith('#') or line.strip().startswith('*'):
                continue

            # Remove inline comments starting with +
            line = re.sub(r'\+.', '', line).rstrip()
            if not line.strip():
                continue

            # Detect rule group header e.g. "NP:" or "VP:"
            header = re.match(r'^(\w+)\s*:', line)
            if header:
                current_tag = header.group(1)
                if current_tag not in rules:
                    rules[current_tag] = []

            # Collect patterns like {<NN>} or {<NP><CC6><NP>}
            if current_tag and '{' in line:
                patterns = re.findall(r'\{[^}]+\}', line)
                for p in patterns:
                    p_clean = re.sub(r'\s+', '', p)
                    rules[current_tag].append(p_clean)

    # Build the final grammar string
    grammar_parts = []
    for tag, patterns in rules.items():
        if patterns:
            unique = list(dict.fromkeys(patterns))
            grammar_parts.append(tag + ": " + "\n  | ".join(unique))

    return "\n".join(grammar_parts)


# ──────────────────────────────────────────────────────────
# FUNCTION 3: check_word_tags()
#
# PURPOSE: Take a sentence and check every word for
#          multiple tags. Report which words are ambiguous.
#
# This is the function that directly answers the question:
# "does this word have more than one possible tag?"
#
# RETURNS: list of dicts, one per word:
#   { 'word': str, 'tags': [list], 'ambiguous': bool }
# ──────────────────────────────────────────────────────────

def check_word_tags(sentence, word_to_tags):
    """
    Checks every word in the sentence against the multi-tag
    dictionary and reports how many tags each word has.

    Words with more than one tag are flagged as ambiguous.
    Words not found in the dictionary get tag ['UNKNOWN'].
    """
    tokens  = sentence.lower().strip().split()
    results = []

    for token in tokens:
        tags = word_to_tags.get(token, ['UNKNOWN'])
        results.append({
            'word':      token,
            'tags':      tags,
            'ambiguous': len(tags) > 1
        })

    return results


# ──────────────────────────────────────────────────────────
# FUNCTION 4: generate_tag_sequences()
#
# PURPOSE: Generate every possible tag sequence for the
#          sentence by combining all tag options for each
#          word using the Cartesian product.
#
# EXAMPLE:
#   "Mosadi wa kgosi o bone kotsi"
#   bone → [VRB, leemedi]
#   All other words → one tag each
#
#   Produces:
#   Sequence 1: NN L31 NN CC4 VRB     NN
#   Sequence 2: NN L31 NN CC4 leemedi NN
#
# RETURNS: list of tagged sequences, each a list of
#          (word, tag) tuples
# ──────────────────────────────────────────────────────────

def generate_tag_sequences(word_tag_info):
    """
    Takes the output of check_word_tags() and generates
    every possible (word, tag) combination for the sentence.

    Uses itertools.product to compute the Cartesian product
    of all tag options across all words.

    Each returned sequence is a list of (word, tag) tuples
    representing one complete tagging of the sentence.
    """
    # Build options list: for each word, list of (word, tag) pairs
    all_options = []
    for entry in word_tag_info:
        word    = entry['word']
        tags    = entry['tags']
        options = [(word, tag) for tag in tags]
        all_options.append(options)

    # Cartesian product gives every combination
    sequences = list(product(*all_options))

    # Convert each tuple of pairs into a list of pairs
    return [list(seq) for seq in sequences]


# ──────────────────────────────────────────────────────────
# FUNCTION 5: parse_sequence()
#
# PURPOSE: Feed one tag sequence to NLTK RegexpParser
#          and return the resulting parse tree.
#
# RETURNS: nltk.Tree object or None if parsing fails
# ──────────────────────────────────────────────────────────

def parse_sequence(tagged_sequence, grammar_string):
    """
    Parses a single tagged sequence using NLTK RegexpParser.
    The grammar_string contains the rules from Parsing Regex.txt.

    Returns the parse tree, or None if the parser fails.
    """
    try:
        parser = nltk.RegexpParser(grammar_string)
        return parser.parse(tagged_sequence)
    except Exception as e:
        return None


# ──────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ──────────────────────────────────────────────────────────

def display_word_tag_check(word_tag_info, sentence):
    """
    Displays the tag check results — showing every word,
    its possible tags, and whether it is ambiguous.
    """
    print("\n" + "=" * 68)
    print(f"  SENTENCE: {sentence}")
    print("=" * 68)
    print("\n  📋 WORD TAG CHECK:")
    print("-" * 68)

    table = []
    for i, entry in enumerate(word_tag_info):
        word      = entry['word']
        tags      = entry['tags']
        ambiguous = "🔀 YES" if entry['ambiguous'] else "  no"
        tag_str   = ", ".join(tags)
        table.append([i + 1, word, tag_str, ambiguous])

    print(tabulate(
        table,
        headers=["#", "Word", "Possible Tags", "Ambiguous?"],
        tablefmt="fancy_grid"
    ))

    ambiguous_words = [e['word'] for e in word_tag_info if e['ambiguous']]
    total_combos    = 1
    for e in word_tag_info:
        total_combos *= len(e['tags'])

    if ambiguous_words:
        print(f"\n  🔀 Ambiguous words: {', '.join(ambiguous_words)}")
        print(f"  📊 Total tag sequences to generate: {total_combos}")
    else:
        print(f"\n  ✅ No ambiguous words — only 1 tag sequence possible.")
    print("=" * 68)


def display_generated_sequences(sequences):
    """
    Displays all generated tag sequences — the different
    ways the sentence can be tagged.
    """
    print(f"\n  🔁 GENERATED TAG SEQUENCES ({len(sequences)} total):")
    print("-" * 68)

    for i, seq in enumerate(sequences, 1):
        tag_line  = " ".join(t for _, t in seq)
        word_line = " ".join(w for w, _ in seq)
        print(f"\n  Sequence {i}:")
        print(f"    Words: {word_line}")
        print(f"    Tags:  {tag_line}")

    print("=" * 68)


def display_parse_results(sequences, grammar_string):
    """
    For each generated tag sequence:
    - Shows the sequence number and tags used
    - Outputs the parse tree in 3 formats:
        a. Bracket notation (text)
        b. Visual ASCII diagram
        c. Python object representation
    - Opens a popup window for each tree
    """
    print(f"\n  🌳 PARSE RESULTS:")
    print("=" * 68)

    parsed_count   = 0
    unparsed_count = 0

    for i, seq in enumerate(sequences, 1):
        tag_line = " ".join(t for _, t in seq)
        print(f"\n  ── Sequence {i}: {tag_line}")
        print("-" * 68)

        tree = parse_sequence(seq, grammar_string)

        if tree is None:
            print("  ⚠️  Parser could not process this sequence.")
            unparsed_count += 1
            continue

        parsed_count += 1

        # Check if tree has any structure or is flat
        has_structure = any(isinstance(child, nltk.Tree) for child in tree)

        # ── a. Bracket notation ───────────────────────────
        print("  a) Bracket Notation:")
        print(f"     {tree}")

        # ── b. Visual ASCII diagram ───────────────────────
        print("\n  b) Visual Tree (ASCII):")
        tree.pretty_print()

        # ── c. Python object representation ───────────────
        print("  c) Python Object Representation:")
        print(f"     Type : {type(tree)}")
        print(f"     Label: {tree.label()}")
        print(f"     Leaves (words): {[w for w, _ in tree.leaves()]}")
        print(f"     Structured: {'Yes' if has_structure else 'No (flat)'}")

        # Show which phrase nodes were built
        if has_structure:
            print("\n  Phrases identified:")
            phrase_table = []
            for subtree in tree.subtrees():
                if subtree != tree and isinstance(subtree, nltk.Tree):
                    words = " ".join(w for w, _ in subtree.leaves())
                    tags  = " ".join(t for _, t in subtree.leaves())
                    phrase_table.append([subtree.label(), words, tags])
            if phrase_table:
                print(tabulate(
                    phrase_table,
                    headers=["Phrase", "Words", "Tags"],
                    tablefmt="simple"
                ))

        print("-" * 68)

        # Open popup window
        tree.draw()

    # Summary
    print(f"\n  📊 PARSE SUMMARY:")
    print(f"     Sequences generated : {len(sequences)}")
    print(f"     Successfully parsed : {parsed_count}")
    print(f"     Could not parse     : {unparsed_count}")
    print("=" * 68)


# ──────────────────────────────────────────────────────────
# MAIN PROGRAM
# ──────────────────────────────────────────────────────────

def main():
    BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS_FILE = os.path.join(BASE_DIR, 'definitions.txt')
    RULES_FILE       = os.path.join(BASE_DIR, 'Parsing Regex.txt')

    print("\n" + "=" * 68)
    print("    🐍 SETSWANA CONSTITUENCY PARSER")
    print("    Multi-Tag Sequence Generator + NLTK Parser")
    print("=" * 68)

    # ── Load multi-tag dictionary ──────────────────────────
    print("\n⏳ Loading definitions ...")
    word_to_tags = load_definitions_multi(DEFINITIONS_FILE)
    ambiguous    = sum(1 for tags in word_to_tags.values() if len(tags) > 1)
    print(f"   ✅ {len(word_to_tags)} words loaded.")
    print(f"   🔀 {ambiguous} words have multiple possible tags.")

    # ── Load grammar rules ─────────────────────────────────
    print("⏳ Loading grammar rules ...")
    grammar_string = load_grammar_rules(RULES_FILE)
    print(f"   ✅ Grammar rules loaded.")

    print("\nType a Setswana sentence and press Enter.")
    print("Type 'exit' to quit.\n")

    while True:
        sentence = input("👉 Sentence: ").strip()

        if not sentence:
            continue
        if sentence.lower() == 'exit':
            print("\nTsamaya sentle! 👋\n")
            break

        # ── STEP 1: Check each word for multiple tags ──────
        word_tag_info = check_word_tags(sentence, word_to_tags)
        display_word_tag_check(word_tag_info, sentence)

        # ── STEP 2: Generate all tag sequences ────────────
        sequences = generate_tag_sequences(word_tag_info)
        display_generated_sequences(sequences)

        # ── STEP 3: Parse each sequence and show results ──
        display_parse_results(sequences, grammar_string)

        print()


if __name__ == '__main__':
    main()
