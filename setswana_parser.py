"""
============================================================
  SETSWANA CONSTITUENCY PARSER
  Uses: definitions.txt + Parsing Regex.txt
  Library: NLTK RegexpParser

  KEY FEATURE: Rule-guided best parse selection
  ─────────────────────────────────────────────
  The parser tries every possible tag combination for
  ambiguous words, scores each valid parse by how well
  it matches the grammar rules provided (deeper structure
  = better score), and selects the BEST parse automatically.
  All alternative parses are shown below for comparison.
============================================================
"""

import re
import os
import nltk
from itertools import product
from tabulate import tabulate


# ─────────────────────────────────────────────────────────
# LABEL MAP — shared across all display functions
# ─────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────
# TAG PRECEDENCE
# When a word has multiple tags, this defines which tag
# is tried FIRST in combination generation. Lower number
# = higher priority = tried first.
# Based on the rule structure in Parsing Regex.txt:
# NP rules expect NN, VP rules expect VRB/VBMD/VBPT, etc.
# ─────────────────────────────────────────────────────────

TAG_PRECEDENCE = {
    # Nouns — highest priority, most rules built around them
    'NN':                1,
    'NN_ng':             2,
    # Core verbs
    'VRB':               3,
    'VBMD':              4,
    'VBPT':              5,
    'VRB_ng':            6,
    'VBMD_ng':           7,
    'VBPT_ng':           8,
    # Modifiers
    'letlhaodi_thito':   9,
    'letlhaodi_tota':    10,
    # Adverbials
    'letlhalosi_mokgwa': 11,
    'letlhalosi_nako':   12,
    'letlhalosi_felo_P': 13,
    'letlhalosi_felo_D': 14,
    'letlhalosi_felo':   15,
    # Pronouns and determiners
    'leemedi':           16,
    'lesupi':            17,
    'lebadi_thito':      18,
    'lesoboki':          19,
    # Particles and concords — lowest, they fill gaps
    'EE1':               20,
    'EE2':               21,
}


# ─────────────────────────────────────────────────────────
# STEP 1A: SINGLE-TAG LOADER
# Returns { 'word': 'FIRST_TAG' } — used for display
# ─────────────────────────────────────────────────────────

def load_definitions(filepath):
    """
    Builds a single-tag dictionary for display purposes.
    Only stores the first/primary tag per word.
    """
    word_to_tag = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            if line.startswith('letlhaodi:') and '{' in line:
                continue

            parts    = line.split(':', 1)
            tag      = parts[0].strip()
            words_str = parts[1].strip().replace(',', '.')
            words    = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                if ' ' in word:
                    continue
                if word not in word_to_tag:
                    word_to_tag[word] = tag

    return word_to_tag


# ─────────────────────────────────────────────────────────
# STEP 1B: MULTI-TAG LOADER
# Returns { 'word': ['TAG1', 'TAG2', ...] }
# Tags are sorted by TAG_PRECEDENCE so higher-priority
# tags are tried first in combination generation.
# ─────────────────────────────────────────────────────────

def load_definitions_multi(filepath):
    """
    Builds a multi-tag dictionary.
    Each word maps to ALL its possible tags, sorted by
    TAG_PRECEDENCE so the most linguistically likely tag
    is always tried first.
    """
    word_to_tags = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            if line.startswith('letlhaodi:') and '{' in line:
                continue

            parts    = line.split(':', 1)
            tag      = parts[0].strip()
            words_str = parts[1].strip().replace(',', '.')
            words    = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                if ' ' in word:
                    continue
                if word not in word_to_tags:
                    word_to_tags[word] = []
                if tag not in word_to_tags[word]:
                    word_to_tags[word].append(tag)

    # Sort each word's tags by TAG_PRECEDENCE
    # Tags not in the precedence table get a default rank of 99
    for word in word_to_tags:
        word_to_tags[word].sort(key=lambda t: TAG_PRECEDENCE.get(t, 99))

    return word_to_tags


# ─────────────────────────────────────────────────────────
# STEP 2: GRAMMAR RULES LOADER
# ─────────────────────────────────────────────────────────

def load_rules(filepath):
    return build_grammar_string(filepath)


def build_grammar_string(filepath):
    """
    Reads the grammar rules file and builds a formatted
    grammar string for NLTK RegexpParser.
    Skips comment lines and plain-text notes.
    """
    rules       = {}
    current_tag = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if not line.strip():
                continue

            # Skip comment/note lines (lines with no braces but plain text)
            if line.strip().startswith('#') or line.strip().startswith('*'):
                continue

            line = re.sub(r'\+.', '', line).rstrip()
            if not line.strip():
                continue

            header_match = re.match(r'^(\w+)\s*:', line)
            if header_match:
                current_tag = header_match.group(1)
                if current_tag not in rules:
                    rules[current_tag] = []

            if current_tag and '{' in line:
                patterns = re.findall(r'\{[^}]+\}', line)
                for p in patterns:
                    p_clean = re.sub(r'\s+', '', p)
                    rules[current_tag].append(p_clean)

    grammar_parts = []
    for tag, patterns in rules.items():
        if patterns:
            unique = list(dict.fromkeys(patterns))
            grammar_parts.append(tag + ": " + "\n  | ".join(unique))

    return "\n".join(grammar_parts)


# ─────────────────────────────────────────────────────────
# STEP 3A: SINGLE-TAG SENTENCE TAGGER (for display)
# ─────────────────────────────────────────────────────────

def tag_sentence(sentence, word_to_tag):
    """
    Tags each word with its primary tag.
    Used for the display table. Unknown words → UNKNOWN.
    """
    tokens = sentence.lower().strip().split()
    return [(token, word_to_tag.get(token, 'UNKNOWN')) for token in tokens]


# ─────────────────────────────────────────────────────────
# STEP 3B: MULTI-TAG COMBINATION GENERATOR
# ─────────────────────────────────────────────────────────

def get_all_tag_combinations(sentence, word_to_tags_multi):
    """
    Generates every possible tag combination for a sentence.
    Because tags are sorted by TAG_PRECEDENCE in load_definitions_multi,
    the first combination tried is always the highest-priority one.

    Example:
      'rata' has tags ['VRB', 'VBMD'] (VRB tried first)
      'bana' has tags ['NN']
      Produces: [('rata','VRB'),('bana','NN')]   ← tried first
                [('rata','VBMD'),('bana','NN')]  ← tried second
    """
    tokens = sentence.lower().strip().split()
    all_options = []
    for token in tokens:
        tags = word_to_tags_multi.get(token, ['UNKNOWN'])
        all_options.append([(token, tag) for tag in tags])
    return list(product(*all_options))


# ─────────────────────────────────────────────────────────
# STEP 4A: SINGLE PARSE
# ─────────────────────────────────────────────────────────

def parse_sentence(tagged_tokens, grammar_string):
    """
    Parses a single tagged token list with NLTK RegexpParser.
    Returns the tree or None on failure.
    """
    try:
        parser = nltk.RegexpParser(grammar_string)
        return parser.parse(tagged_tokens)
    except Exception as e:
        print(f"\n  Parser error: {e}")
        return None


# ─────────────────────────────────────────────────────────
# STEP 4B: SCORE A TREE
# Higher score = more phrase structure = better parse.
# This reflects how well the parse matches the grammar rules
# because rules only fire when patterns match — so more
# nodes means more rules were successfully applied.
# ─────────────────────────────────────────────────────────

def score_tree(tree):
    """
    Scores a parse tree based on:
    1. Number of phrase nodes (each matched rule = +2)
    2. Depth of nesting (deeper = more structure = +1 per level)
    3. Penalty for UNKNOWN tags (each unknown = -3)

    This reflects rule-guided selection: a tree with more
    phrase nodes had more grammar rules fire successfully,
    meaning the tag combination matched the provided rules better.
    """
    if tree is None:
        return -999

    phrase_count = 0
    depth_total  = 0
    unknown_penalty = 0

    def traverse(subtree, depth):
        nonlocal phrase_count, depth_total, unknown_penalty
        if isinstance(subtree, nltk.Tree):
            if subtree != tree:  # don't count root S
                phrase_count += 1
                depth_total  += depth
            for child in subtree:
                traverse(child, depth + 1)
        else:
            # subtree is a (word, tag) leaf
            if subtree[1] == 'UNKNOWN':
                unknown_penalty += 3

    traverse(tree, 0)
    return (phrase_count * 2) + depth_total - unknown_penalty


# ─────────────────────────────────────────────────────────
# STEP 4C: FULL AMBIGUITY PARSER WITH BEST PARSE SELECTION
# ─────────────────────────────────────────────────────────

def parse_with_ambiguity(sentence, word_to_tags_multi, grammar_string):
    """
    Core parser with rule-guided best parse selection:

    1. Generates all tag combinations (sorted by TAG_PRECEDENCE)
    2. Parses each combination with NLTK RegexpParser
    3. Keeps only structured parses (at least one phrase node)
    4. Scores each parse by how many grammar rules fired
    5. Returns parses sorted best-first, with scores attached

    Returns list of (score, tagged_tokens, tree), best first.
    """
    try:
        parser = nltk.RegexpParser(grammar_string)
    except Exception as e:
        print(f"\n  Grammar error: {e}")
        return []

    combinations = get_all_tag_combinations(sentence, word_to_tags_multi)
    valid_parses = []
    seen_trees   = set()

    for tagged_combo in combinations:
        try:
            tree = parser.parse(tagged_combo)

            # Only keep trees with at least one phrase node
            has_structure = any(
                isinstance(child, nltk.Tree) for child in tree
            )
            if not has_structure:
                continue

            tree_str = str(tree)
            if tree_str in seen_trees:
                continue
            seen_trees.add(tree_str)

            score = score_tree(tree)
            valid_parses.append((score, list(tagged_combo), tree))

        except Exception:
            continue

    # Sort by score descending — best (highest score) first
    valid_parses.sort(key=lambda x: x[0], reverse=True)
    return valid_parses


# ─────────────────────────────────────────────────────────
# STEP 5: DISPLAY FUNCTIONS
# ─────────────────────────────────────────────────────────

def display_tagging(tagged_tokens, sentence, word_to_tags_multi=None):
    """
    Prints the word → POS tag table.
    Shows alternative tags for ambiguous words if multi-dict provided.
    """
    print("\n" + "=" * 68)
    print(f"  SENTENCE: {sentence}")
    print("=" * 68)

    table = []
    for i, (word, tag) in enumerate(tagged_tokens):
        label    = LABEL_MAP.get(tag, tag)
        alt_tags = ""
        if word_to_tags_multi:
            all_tags = word_to_tags_multi.get(word, [tag])
            others   = [t for t in all_tags if t != tag]
            if others:
                alt_tags = "also: " + ", ".join(others)
        table.append([i + 1, word, tag, label, alt_tags])

    headers = ["#", "Lefoko (Word)", "Primary Tag", "Tlhaloso (Meaning)", "Alt Tags"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def display_constituents(tagged_tokens):
    """Groups words by their constituent type."""
    groups = {}
    for word, tag in tagged_tokens:
        groups.setdefault(tag, []).append(word)

    print("\n CONSTITUENCY BREAKDOWN (Primary Tags):")
    print("-" * 68)

    friendly = {
        'VRB':               ' Leamanyi — Verbs',
        'VRB_ng':            ' Leamanyi_ng — Verbs (-ng form)',
        'VBMD':              ' Leamanyi — Mood Verbs',
        'VBPT':              ' Leamanyi — Past Tense Verbs',
        'NN':                ' Lerui — Nouns',
        'NN_ng':             ' Lerui_ng — Nouns (-ng form)',
        'letlhaodi_thito':   ' Letlhaodi — Adjective/Adverb',
        'letlhaodi_tota':    ' Letlhaodi_tota — Intensifier',
        'letlhalosi_mokgwa': ' Letlhalosi Mokgwa — Manner',
        'letlhalosi_nako':   ' Letlhalosi Nako — Time',
        'letlhalosi_felo_P': ' Letlhalosi Felo — Place',
        'leemedi':           ' Leemedi — Pronoun',
        'lesupi':            ' Lesupi — Demonstrative',
        'lebadi_thito':      ' Lebadi — Quantifier/Number',
        'lesoboki':          ' Lesoboki — Totality',
        'UNKNOWN':           ' Ga go itsege — Unknown',
    }

    for tag, words in groups.items():
        label = friendly.get(tag, f' {tag}')
        print(f"  {label}: {', '.join(words)}")
    print("=" * 68)


def display_ambiguity_report(sentence, word_to_tags_multi):
    """Reports ambiguous words and total combinations to be tried."""
    tokens    = sentence.lower().strip().split()
    ambiguous = [
        (t, word_to_tags_multi.get(t, ['UNKNOWN']))
        for t in tokens
        if len(word_to_tags_multi.get(t, ['UNKNOWN'])) > 1
    ]

    if ambiguous:
        print("\n   AMBIGUOUS WORDS:")
        print("-" * 68)
        for word, tags in ambiguous:
            ordered = sorted(tags, key=lambda t: TAG_PRECEDENCE.get(t, 99))
            print(f"  '{word}' → possible tags (in priority order): {', '.join(ordered)}")

        total_combos = 1
        for token in tokens:
            total_combos *= len(word_to_tags_multi.get(token, ['UNKNOWN']))
        print(f"\n  Total tag combinations to try: {total_combos}")
        print("=" * 68)
    else:
        print("\n  No ambiguous words — each word has exactly one tag.")
        print("=" * 68)


def display_best_parse(score, tagged_combo, tree):
    """
    Displays the best (highest scoring) parse tree with full explanation
    of why it was selected — showing which rules matched.
    """
    print("\n" + "=" * 68)
    print(f"  BEST PARSE  (Rule-Match Score: {score})")
    print("=" * 68)

    # Show the tag combination that produced this parse
    print("\n  Tags used for this parse:")
    tag_table = [[w, t, LABEL_MAP.get(t, t)] for w, t in tagged_combo]
    print(tabulate(tag_table, headers=["Word", "Tag", "Meaning"], tablefmt="simple"))

    # Show which phrase nodes were built (= which rules fired)
    print("\n  Grammar rules that matched:")
    print("-" * 68)
    matched_rules = []
    for subtree in tree.subtrees():
        if subtree != tree and isinstance(subtree, nltk.Tree):
            words = " ".join(w for w, _ in subtree.leaves())
            tags  = " ".join(t for _, t in subtree.leaves())
            matched_rules.append([subtree.label(), words, tags])
    if matched_rules:
        print(tabulate(
            matched_rules,
            headers=["Phrase", "Words", "Tags matched"],
            tablefmt="simple"
        ))
    else:
        print("  (no phrase rules fired)")

    print(f"\n  BEST PARSE — Bracket Notation:")
    print("-" * 68)
    print(tree)

    print(f"\n  BEST PARSE — Visual Tree:")
    print("-" * 68)
    tree.pretty_print()
    print("=" * 68)
    tree.draw()


def display_alternative_parses(alternatives):
    """
    Displays all alternative parses below the best one,
    with their scores and tag combinations for comparison.
    """
    if not alternatives:
        return

    print(f"\n  ALTERNATIVE PARSES ({len(alternatives)} other valid combination(s)):")
    print("=" * 68)

    for i, (score, tagged_combo, tree) in enumerate(alternatives, 2):
        print(f"\n  — Alternative Parse {i}  (Score: {score})")
        print("-" * 68)

        tags_used = "  |  ".join(f"{w}→{t}" for w, t in tagged_combo)
        print(f"  Tags: {tags_used}")

        print(f"\n  Visual Tree:")
        tree.pretty_print()
        print("-" * 68)


def display_fallback_tree(tree, tagged):
    """Shown when no structured parse is found — displays flat default."""
    print("\n   No structured parse found across any tag combination.")
    print("      Showing default flat parse with primary tags:\n")
    if tree:
        tree.pretty_print()
    else:
        print("  (Parser could not build any tree)")
    print("=" * 68)


# ─────────────────────────────────────────────────────────
# STEP 6: MAIN PROGRAM
# ─────────────────────────────────────────────────────────

def main():
    BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
    DEFINITIONS_FILE = os.path.join(BASE_DIR, 'definitions.txt')
    RULES_FILE       = os.path.join(BASE_DIR, 'Parsing Regex.txt')

    print("\n" + "=" * 68)
    print("    SETSWANA CONSTITUENCY PARSER")
    print("    Powered by NLTK + Definitions & Grammar Rules")
    print("    Rule-Guided Best Parse Selection: ENABLED")
    print("=" * 68)

    # Load single-tag dict (for display)
    print("\n Loading definitions (single-tag) ...")
    word_to_tag = load_definitions(DEFINITIONS_FILE)
    print(f"   {len(word_to_tag)} words loaded.")

    # Load multi-tag dict (for ambiguity resolution)
    print(" Loading definitions (multi-tag) ...")
    word_to_tags_multi = load_definitions_multi(DEFINITIONS_FILE)
    ambiguous_count = sum(
        1 for tags in word_to_tags_multi.values() if len(tags) > 1
    )
    print(f"   {len(word_to_tags_multi)} words loaded.")
    print(f"   {ambiguous_count} words have multiple possible tags.")

    # Load grammar rules
    print(" Loading grammar rules ...")
    grammar_string = load_rules(RULES_FILE)
    print(f"   Grammar rules loaded successfully.")

    print("\nType a Setswana sentence and press Enter.")
    print("Type 'exit' to quit.\n")

    while True:
        sentence = input(" Sentence: ").strip()

        if not sentence:
            continue
        if sentence.lower() == 'exit':
            print("\nTsamaya sentle! \n")
            break

        # ── 1. Tag with primary tags (for display) ────────
        tagged = tag_sentence(sentence, word_to_tag)

        # ── 2. Show tagging table with alt tags ───────────
        display_tagging(tagged, sentence, word_to_tags_multi)

        # ── 3. Show constituency breakdown ────────────────
        display_constituents(tagged)

        # ── 4. Report ambiguous words ─────────────────────
        display_ambiguity_report(sentence, word_to_tags_multi)

        # ── 5. Try all combinations, score and rank ───────
        print("\n Parsing all tag combinations ...")
        valid_parses = parse_with_ambiguity(
            sentence, word_to_tags_multi, grammar_string
        )

        if not valid_parses:
            # No structured parse found — show flat fallback
            fallback = parse_sentence(tagged, grammar_string)
            display_fallback_tree(fallback, tagged)
        else:
            print(f"   Found {len(valid_parses)} structured parse(s).\n")

            # ── 6. Display best parse with full explanation ──
            best_score, best_combo, best_tree = valid_parses[0]
            display_best_parse(best_score, best_combo, best_tree)

            # ── 7. Display alternatives below ────────────────
            display_alternative_parses(valid_parses[1:])

        print()


if __name__ == '__main__':
    main()
