"""
============================================================
  SETSWANA CONSTITUENCY PARSER
  Uses: definitions.txt + Parsing_rules_testing.txt
  Library: NLTK RegexpParser
============================================================
"""

import re
import nltk
from tabulate import tabulate

# ─────────────────────────────────────────────────────────
# STEP 1: READ AND PARSE THE DEFINITIONS FILE
# This loads every word and maps it to its POS tag
# ─────────────────────────────────────────────────────────

def load_definitions(filepath):
    """
    Reads definitions.txt and builds a dictionary:
    { 'word': 'TAG', ... }
    Each line looks like:  TAG:word1.word2.word3.
    """
    word_to_tag = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines or lines without a colon
            if not line or ':' not in line:
                continue

            # Skip the inline grammar rule at the bottom
            if line.startswith('letlhaodi:') and '{' in line:
                continue

            # Split on FIRST colon only → gives us (TAG, words)
            parts = line.split(':', 1)
            tag = parts[0].strip()
            words_str = parts[1].strip()

            # Words are separated by dots (.)
            # Some entries also use commas — handle both
            words_str = words_str.replace(',', '.')
            words = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                # Some words have spaces (multi-word expressions) — skip for now
                if ' ' in word:
                    continue
                # Don't overwrite if already tagged with a more specific tag
                if word not in word_to_tag:
                    word_to_tag[word] = tag

    return word_to_tag


# ─────────────────────────────────────────────────────────
# STEP 2: READ AND PARSE THE RULES FILE
# This loads the grammar rules for NLTK RegexpParser
# ─────────────────────────────────────────────────────────

def load_rules(filepath):
    """
    Reads Parsing_rules_testing.txt and extracts valid
    NLTK RegexpParser grammar rules.

    Rules look like:
        NP: {<NN>}
            {<NP><CC6><NP>}
    """
    grammar_lines = []
    current_tag = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()

            # Skip empty lines and comment-like lines
            if not line.strip():
                continue
            if line.strip().startswith('#') or line.strip().startswith('*'):
                continue

            # Remove inline comments like  ***** remove
            line = re.sub(r'\*+.*', '', line).rstrip()
            if not line.strip():
                continue

            # Detect a new rule header like "NP:", "VP:", "leamanyi:"
            header_match = re.match(r'^(\w+)\s*:', line)
            if header_match:
                current_tag = header_match.group(1)

            # Only keep lines that have valid chunk patterns { ... }
            if '{' in line and '>' in line and current_tag:
                # Extract just the pattern part {<...>}
                pattern_match = re.search(r'\{[^}]+\}', line)
                if pattern_match:
                    pattern = pattern_match.group(0)
                    grammar_lines.append(f"  {pattern}")

    # Build the full grammar string grouped by tag
    # We need to rebuild it properly per tag
    return build_grammar_string(filepath)


def build_grammar_string(filepath):
    """
    Rebuilds grammar rules grouped under each tag name,
    formatted exactly as NLTK RegexpParser expects.
    """
    rules = {}         # { 'NP': ['{<NN>}', '{<NP><CC6><NP>}', ...] }
    current_tag = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if not line.strip():
                continue

            # Remove inline comments
            line = re.sub(r'\*+.*', '', line).rstrip()
            if not line.strip():
                continue

            # New rule block header
            header_match = re.match(r'^(\w+)\s*:', line)
            if header_match:
                current_tag = header_match.group(1)
                if current_tag not in rules:
                    rules[current_tag] = []

            # Collect patterns
            if current_tag and '{' in line:
                # Find all patterns on this line
                patterns = re.findall(r'\{[^}]+\}', line)
                for p in patterns:
                    # Clean up spacing inside pattern
                    p_clean = re.sub(r'\s+', '', p)
                    rules[current_tag].append(p_clean)

    # Build the grammar string
    grammar_parts = []
    for tag, patterns in rules.items():
        if patterns:
            unique_patterns = list(dict.fromkeys(patterns))  # remove duplicates
            rule_str = tag + ": " + "\n  | ".join(unique_patterns)
            grammar_parts.append(rule_str)

    return "\n".join(grammar_parts)


# ─────────────────────────────────────────────────────────
# STEP 3: TAG A SENTENCE
# Looks up each word in our definitions dictionary
# ─────────────────────────────────────────────────────────

def tag_sentence(sentence, word_to_tag):
    """
    Takes a sentence string and returns a list of (word, TAG) tuples.
    Words not found in dictionary get tag 'UNKNOWN'.
    """
    tokens = sentence.lower().strip().split()
    tagged = []
    for token in tokens:
        tag = word_to_tag.get(token, 'UNKNOWN')
        tagged.append((token, tag))
    return tagged


# ─────────────────────────────────────────────────────────
# STEP 4: RUN THE NLTK PARSER
# ─────────────────────────────────────────────────────────

def parse_sentence(tagged_tokens, grammar_string):
    """
    Uses NLTK RegexpParser with our loaded grammar rules
    to build a parse tree from the tagged tokens.
    """
    try:
        parser = nltk.RegexpParser(grammar_string)
        tree = parser.parse(tagged_tokens)
        return tree
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────────────────
# STEP 5: DISPLAY RESULTS
# ─────────────────────────────────────────────────────────

def display_tagging(tagged_tokens, sentence):
    """Prints a clean table of word → POS tag mappings."""

    # Human-readable label map
    label_map = {
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
        'UNKNOWN':           '⚠ Ga go itsege (Unknown)',
    }

    # Add CC and L tags
    for i in range(1, 16):
        key = f'CC{i}' if i <= 9 else f'C{i}'
        label_map[key] = f'Kgokagano {key} (Concord/Connector)'
    for i in range(1, 63):
        label_map[f'L{i:02d}'] = f'Karolo L{i:02d} (Particle/Morpheme)'

    print("\n" + "=" * 65)
    print(f"  SENTENCE: {sentence}")
    print("=" * 65)

    table = []
    for i, (word, tag) in enumerate(tagged_tokens):
        label = label_map.get(tag, tag)
        table.append([i + 1, word, tag, label])

    headers = ["#", "Lefoko (Word)", "Tag", "Tlhaloso (Meaning)"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def display_constituents(tagged_tokens):
    """Groups words by their constituent type."""

    groups = {}
    for word, tag in tagged_tokens:
        if tag not in groups:
            groups[tag] = []
        groups[tag].append(word)

    print("\n  📌 CONSTITUENCY BREAKDOWN:")
    print("-" * 65)

    friendly = {
        'VRB':               '🟢 Leamanyi — Verbs',
        'VRB_ng':            '🟢 Leamanyi_ng — Verbs (-ng form)',
        'VBMD':              '🟢 Leamanyi — Mood Verbs',
        'VBPT':              '🟢 Leamanyi — Past Tense Verbs',
        'NN':                '🔵 Lerui — Nouns',
        'NN_ng':             '🔵 Lerui_ng — Nouns (-ng form)',
        'letlhaodi_thito':   '🟡 Letlhaodi — Adjective/Adverb',
        'letlhaodi_tota':    '🟡 Letlhaodi_tota — Intensifier',
        'letlhalosi_mokgwa': '🟠 Letlhalosi Mokgwa — Manner',
        'letlhalosi_nako':   '🟠 Letlhalosi Nako — Time',
        'letlhalosi_felo_P': '🟠 Letlhalosi Felo — Place',
        'leemedi':           '🟣 Leemedi — Pronoun',
        'lesupi':            '🟣 Lesupi — Demonstrative',
        'lebadi_thito':      '🟤 Lebadi — Quantifier/Number',
        'lesoboki':          '🟤 Lesoboki — Totality',
        'UNKNOWN':           '❓ Ga go itsege — Unknown',
    }

    for tag, words in groups.items():
        label = friendly.get(tag, f'📎 {tag}')
        print(f"  {label}: {', '.join(words)}")

    print("=" * 65)


def display_tree(tree):
    """
    Displays the NLTK parse tree in 3 different ways:

    WAY 1 — Flat text:     (S (NP kgosi/NN) reka/VRB (NP koloi/NN))
    WAY 2 — ASCII diagram: draws the tree as branches in the terminal
    WAY 3 — Visual popup:  opens a real graphical tree window (requires tkinter)
    """
    if not tree:
        print("  ⚠️  No tree to display.")
        return

    # ── WAY 1: Flat one-line text representation ──────────────
    print("\n  🌳 TREE — WAY 1: Flat Text")
    print("-" * 65)
    print(" ", tree)                      # prints: (S (NP kgosi/NN) reka/VRB ...)

    # ── WAY 2: ASCII diagram in the terminal ──────────────────
    print("\n  🌳 TREE — WAY 2: ASCII Diagram")
    print("-" * 65)
    tree.pretty_print()                   # draws branches using | and _ characters

    # ── WAY 3: Visual popup window ────────────────────────────
    print("\n  🌳 TREE — WAY 3: Visual Popup Window")
    print("-" * 65)
    try:
        tree.draw()                       # opens a tkinter GUI window with the tree
        print("  ✅ Tree window opened! Close it to continue.")
    except Exception:
        print("  ⚠️  Visual window unavailable in this environment.")
        print("      Run the code on your own computer to see the popup tree.")

    print("=" * 65)


# ─────────────────────────────────────────────────────────
# STEP 6: MAIN PROGRAM — Bring it all together
# ─────────────────────────────────────────────────────────

def main():
    # File paths — adjust if needed
    DEFINITIONS_FILE = '/mnt/user-data/uploads/definitions.txt'
    RULES_FILE       = '/mnt/user-data/uploads/Parsing_rules_testing.txt'

    print("\n" + "=" * 65)
    print("   🐍 SETSWANA CONSTITUENCY PARSER")
    print("   Powered by NLTK + Your Definitions & Rules Files")
    print("=" * 65)

    # Load files
    print("\n⏳ Loading definitions from definitions.txt ...")
    word_to_tag = load_definitions(DEFINITIONS_FILE)
    print(f"   ✅ Loaded {len(word_to_tag)} word definitions.")

    print("⏳ Loading grammar rules from Parsing_rules_testing.txt ...")
    grammar_string = load_rules(RULES_FILE)
    print(f"   ✅ Grammar rules loaded successfully.")

    print("\nType a Setswana sentence and press Enter.")
    print("Type 'exit' to quit.\n")

    while True:
        sentence = input("👉 Sentence: ").strip()

        if not sentence:
            continue
        if sentence.lower() == 'exit':
            print("\nTsamaya sentle! 👋\n")
            break

        # Tag the words
        tagged = tag_sentence(sentence, word_to_tag)

        # Display the tagging table
        display_tagging(tagged, sentence)

        # Display constituency groups
        display_constituents(tagged)

        # Run the NLTK parser and display tree
        tree = parse_sentence(tagged, grammar_string)
        display_tree(tree)

        print()


if __name__ == '__main__':
    main()
