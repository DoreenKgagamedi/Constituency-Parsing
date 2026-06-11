"""
============================================================
  SETSWANA CONSTITUENCY PARSER
  Uses: definitions.txt + Parsing Regex.txt
  Library: NLTK RegexpParser

  KEY FEATURES:
  ─────────────────────────────────────────────────────────
  1. Multi-tag ambiguity resolution — every word's possible
     tags are loaded from definitions.txt. For ambiguous
     words, all tag combinations are tried.

  2. Rule-guided tag precedence — the grammar rules file
     is read and each tag is counted across all rules.
     Tags that appear more in the rules file are treated
     as higher priority. The rules file itself determines
     precedence, not a hardcoded list.

  3. Context-based tag resolution — for ambiguous words,
     the system reads the rules file and checks which tag
     best fits the neighbouring words in the sentence.
     The tag whose rules best match the surrounding context
     is selected as the best candidate.

  4. Best parse selection — all valid parses are scored
     by how many grammar rules fired. The highest scoring
     parse (most rule matches) is shown first. All
     alternatives are shown below for comparison.
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
# FALLBACK TAG PRECEDENCE
# Used only if the rules file cannot be read.
# Under normal operation, precedence is learned directly
# from the rules file by build_tag_precedence_from_rules().
# ─────────────────────────────────────────────────────────

TAG_PRECEDENCE = {
    'NN': 1, 'NN_ng': 2,
    'VRB': 3, 'VBMD': 4, 'VBPT': 5,
    'VRB_ng': 6, 'VBMD_ng': 7, 'VBPT_ng': 8,
    'letlhaodi_thito': 9, 'letlhaodi_tota': 10,
    'letlhalosi_mokgwa': 11, 'letlhalosi_nako': 12,
    'letlhalosi_felo_P': 13, 'letlhalosi_felo_D': 14,
    'letlhalosi_felo': 15,
    'leemedi': 16, 'lesupi': 17,
    'lebadi_thito': 18, 'lesoboki': 19,
    'EE1': 20, 'EE2': 21,
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

            parts     = line.split(':', 1)
            tag       = parts[0].strip()
            words_str = parts[1].strip().replace(',', '.')
            words     = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                if ' ' in word:
                    continue
                if word not in word_to_tag:
                    word_to_tag[word] = tag

    return word_to_tag


# ─────────────────────────────────────────────────────────
# STEP 1B: MULTI-TAG LOADER
# Returns { 'word': ['TAG1', 'TAG2', ...] }
# Tags sorted by the precedence passed in — which is learned
# from the rules file, not hardcoded.
# ─────────────────────────────────────────────────────────

def load_definitions_multi(filepath, tag_precedence=None):
    """
    Builds a multi-tag dictionary where every word maps to
    ALL its possible tags from definitions.txt.

    Tags are sorted by tag_precedence (learned from the rules
    file) so higher-priority tags are tried first when
    generating combinations. Falls back to TAG_PRECEDENCE
    if no precedence dict is passed in.
    """
    precedence   = tag_precedence or TAG_PRECEDENCE
    word_to_tags = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            if line.startswith('letlhaodi:') and '{' in line:
                continue

            parts     = line.split(':', 1)
            tag       = parts[0].strip()
            words_str = parts[1].strip().replace(',', '.')
            words     = [w.strip().lower() for w in words_str.split('.') if w.strip()]

            for word in words:
                if ' ' in word:
                    continue
                if word not in word_to_tags:
                    word_to_tags[word] = []
                if tag not in word_to_tags[word]:
                    word_to_tags[word].append(tag)

    # Sort by rules-derived precedence — most rule-frequent tag first
    for word in word_to_tags:
        word_to_tags[word].sort(key=lambda t: precedence.get(t, 999))

    return word_to_tags


# ─────────────────────────────────────────────────────────
# STEP 2A: GRAMMAR STRING BUILDER
# Formats rules for NLTK RegexpParser
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
# STEP 2B: RULES DICTIONARY BUILDER  ← NEW
# Builds a searchable dict from the rules file.
# Used by resolve_tag_from_rules() to look up which rules
# contain a given tag and its neighbours.
# ─────────────────────────────────────────────────────────

def build_rules_dict(filepath):
    """
    Reads the grammar rules file and returns a structured
    dictionary of all rules:

    {
      'NP': ['{<NN>}', '{<NP><CC6><NP>}', ...],
      'VP': ['{<VP><NP>}', ...],
      ...
    }

    This is used by resolve_tag_from_rules() to search
    which rules contain a particular tag and check whether
    the neighbouring tags in the sentence also appear in
    the same rule pattern — giving context-based resolution.
    """
    rules_dict  = {}
    current_tag = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            if not line.strip():
                continue
            if line.strip().startswith('#') or line.strip().startswith('*'):
                continue

            line = re.sub(r'\+.', '', line).rstrip()
            if not line.strip():
                continue

            header = re.match(r'^(\w+)\s*:', line)
            if header:
                current_tag = header.group(1)
                if current_tag not in rules_dict:
                    rules_dict[current_tag] = []

            if current_tag and '{' in line:
                patterns = re.findall(r'\{[^}]+\}', line)
                for p in patterns:
                    p_clean = re.sub(r'\s+', '', p)
                    if p_clean not in rules_dict[current_tag]:
                        rules_dict[current_tag].append(p_clean)

    return rules_dict


# ─────────────────────────────────────────────────────────
# STEP 2C: TAG PRECEDENCE FROM RULES FILE  ← NEW
# Learns which tags are most important by counting how often
# each tag appears across all rules in the grammar file.
# This replaces the hardcoded TAG_PRECEDENCE with one derived
# directly from the rules file structure.
# ─────────────────────────────────────────────────────────

def build_tag_precedence_from_rules(filepath):
    """
    Reads the grammar rules file and counts how many times
    each tag appears across all rule patterns.

    Tags that appear more frequently in the rules are more
    central to the grammar — so they get higher precedence
    (lower rank number = tried first when resolving ambiguity).

    This means the RULES FILE itself determines tag priority,
    not our manual assumptions.

    Returns:
        precedence  — { 'tag': rank } where rank 1 = highest priority
        tag_counts  — { 'tag': count } raw frequency counts
    """
    tag_counts = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if '{' not in line or '>' not in line:
                continue
            if line.strip().startswith('*') or line.strip().startswith('#'):
                continue
            # Extract all tag names inside < > brackets
            tags_in_line = re.findall(r'<(\w+)', line)
            for tag in tags_in_line:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by frequency descending — most frequent = rank 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
    precedence  = {tag: rank + 1 for rank, (tag, _) in enumerate(sorted_tags)}

    return precedence, tag_counts


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
# STEP 3B: CONTEXT-BASED TAG RESOLVER  ← NEW
# For ambiguous words, reads the rules file and checks which
# tag best fits the neighbouring words in the sentence.
# ─────────────────────────────────────────────────────────

def resolve_tag_from_rules(word, possible_tags, sentence_tags, position, rules_dict):
    """
    Resolves an ambiguous word's tag by consulting the grammar
    rules file and the surrounding words in the sentence.

    How it works:
    1. For each possible tag, searches every rule in rules_dict
    2. Checks if that tag appears in any rule pattern
    3. If it does, checks whether the LEFT and RIGHT neighbouring
       words' tags also appear in the SAME rule pattern
    4. Neighbour matches score +2 each (strong context signal)
    5. Appearing in a rule at all scores +1 (weak signal)
    6. The tag with the highest total score is selected

    This means the grammar rules directly determine which tag
    is chosen — not a hardcoded list.

    Parameters:
        word          — the ambiguous word being resolved
        possible_tags — list of its possible tags e.g. ['VRB','VBMD']
        sentence_tags — full sentence as [(word,tag),...] with primary tags
        position      — index of this word in sentence_tags
        rules_dict    — built by build_rules_dict()

    Returns the best matching tag string.
    """
    tag_scores = {tag: 0 for tag in possible_tags}

    # Get left and right neighbour tags from the sentence
    left_tag  = sentence_tags[position - 1][1] if position > 0 else None
    right_tag = sentence_tags[position + 1][1] if position < len(sentence_tags) - 1 else None

    # Search every rule in the rules file
    for phrase_label, patterns in rules_dict.items():
        for pattern in patterns:
            # Extract the ordered tag sequence from the pattern
            # e.g. '{<NN><VRB>}' → ['NN', 'VRB']
            # e.g. '{<NN|leemedi><VRB>}' → ['NN|leemedi', 'VRB']
            tags_in_pattern = re.findall(r'<([^>]+)>', pattern)

            for candidate_tag in possible_tags:
                for i, tag_slot in enumerate(tags_in_pattern):
                    # Handle alternatives like <NN|VRB|leemedi>
                    slot_options = tag_slot.split('|')

                    if candidate_tag not in slot_options:
                        continue

                    # Candidate tag appears in this rule — weak signal
                    neighbour_score = 1

                    # Check left neighbour against slot to the left
                    if left_tag and i > 0:
                        left_slot = tags_in_pattern[i - 1].split('|')
                        if left_tag in left_slot:
                            neighbour_score += 2  # strong context match

                    # Check right neighbour against slot to the right
                    if right_tag and i < len(tags_in_pattern) - 1:
                        right_slot = tags_in_pattern[i + 1].split('|')
                        if right_tag in right_slot:
                            neighbour_score += 2  # strong context match

                    tag_scores[candidate_tag] += neighbour_score

    # Select tag with highest score
    # If tied, the first tag wins (already sorted by rules-derived precedence)
    best_tag = max(tag_scores, key=lambda t: tag_scores[t])

    return best_tag, tag_scores


# ─────────────────────────────────────────────────────────
# STEP 3C: RESOLVE FULL SENTENCE TAGS
# Applies resolve_tag_from_rules() to every ambiguous word
# in the sentence, producing a fully resolved tag list.
# ─────────────────────────────────────────────────────────

def resolve_sentence_tags(sentence, word_to_tag, word_to_tags_multi, rules_dict):
    """
    Tags every word in the sentence, then for any word with
    multiple possible tags, uses the grammar rules and sentence
    context to pick the best tag.

    Returns:
        resolved     — [(word, best_tag), ...] for full sentence
        resolutions  — list of resolution detail dicts for display
    """
    primary_tagged = tag_sentence(sentence, word_to_tag)
    resolved       = list(primary_tagged)
    resolutions    = []

    for i, (word, primary_tag) in enumerate(primary_tagged):
        all_tags = word_to_tags_multi.get(word, [primary_tag])

        if len(all_tags) > 1:
            best_tag, tag_scores = resolve_tag_from_rules(
                word, all_tags, primary_tagged, i, rules_dict
            )
            resolved[i] = (word, best_tag)
            resolutions.append({
                'word':       word,
                'position':   i,
                'all_tags':   all_tags,
                'scores':     tag_scores,
                'selected':   best_tag,
                'left_ctx':   primary_tagged[i-1] if i > 0 else None,
                'right_ctx':  primary_tagged[i+1] if i < len(primary_tagged)-1 else None,
            })

    return resolved, resolutions


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
# ─────────────────────────────────────────────────────────

def score_tree(tree):
    """
    Scores a parse tree:
    +2 per phrase node  (each matched grammar rule)
    +1 per nesting level (deeper = more rules chained)
    -3 per UNKNOWN tag  (penalise unrecognised words)
    """
    if tree is None:
        return -999

    phrase_count    = 0
    depth_total     = 0
    unknown_penalty = 0

    def traverse(subtree, depth):
        nonlocal phrase_count, depth_total, unknown_penalty
        if isinstance(subtree, nltk.Tree):
            if subtree != tree:
                phrase_count += 1
                depth_total  += depth
            for child in subtree:
                traverse(child, depth + 1)
        else:
            if subtree[1] == 'UNKNOWN':
                unknown_penalty += 3

    traverse(tree, 0)
    return (phrase_count * 2) + depth_total - unknown_penalty


# ─────────────────────────────────────────────────────────
# STEP 4C: MULTI-TAG COMBINATION GENERATOR
# ─────────────────────────────────────────────────────────

def get_all_tag_combinations(sentence, word_to_tags_multi):
    """
    Generates every possible tag combination for the sentence.
    Tags are already sorted by rules-derived precedence, so
    the first combination tried is always the highest-priority.
    """
    tokens = sentence.lower().strip().split()
    all_options = []
    for token in tokens:
        tags = word_to_tags_multi.get(token, ['UNKNOWN'])
        all_options.append([(token, tag) for tag in tags])
    return list(product(*all_options))


# ─────────────────────────────────────────────────────────
# STEP 4D: FULL AMBIGUITY PARSER WITH BEST PARSE SELECTION
# ─────────────────────────────────────────────────────────

def parse_with_ambiguity(sentence, word_to_tags_multi, grammar_string):
    """
    Tries every tag combination, scores each valid parse,
    and returns all structured parses sorted best-first.
    Returns list of (score, tagged_tokens, tree).
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
            has_structure = any(isinstance(c, nltk.Tree) for c in tree)
            if not has_structure:
                continue
            tree_str = str(tree)
            if tree_str in seen_trees:
                continue
            seen_trees.add(tree_str)
            valid_parses.append((score_tree(tree), list(tagged_combo), tree))
        except Exception:
            continue

    valid_parses.sort(key=lambda x: x[0], reverse=True)
    return valid_parses


# ─────────────────────────────────────────────────────────
# STEP 5: DISPLAY FUNCTIONS
# ─────────────────────────────────────────────────────────

def display_tagging(tagged_tokens, sentence, word_to_tags_multi=None):
    """Prints the word → POS tag table with alternative tags shown."""
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

    print(tabulate(table,
                   headers=["#", "Lefoko (Word)", "Primary Tag",
                             "Tlhaloso (Meaning)", "Alt Tags"],
                   tablefmt="fancy_grid"))


def display_constituents(tagged_tokens):
    """Groups words by their constituent type."""
    groups = {}
    for word, tag in tagged_tokens:
        groups.setdefault(tag, []).append(word)

    print("\n  📌 CONSTITUENCY BREAKDOWN (Primary Tags):")
    print("-" * 68)

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
        print(f"  {friendly.get(tag, f'📎 {tag}')}: {', '.join(words)}")
    print("=" * 68)


def display_ambiguity_report(sentence, word_to_tags_multi, tag_precedence):
    """Reports ambiguous words and total combinations to be tried."""
    tokens    = sentence.lower().strip().split()
    ambiguous = [
        (t, word_to_tags_multi.get(t, ['UNKNOWN']))
        for t in tokens
        if len(word_to_tags_multi.get(t, ['UNKNOWN'])) > 1
    ]

    if ambiguous:
        print("\n  🔀 AMBIGUOUS WORDS:")
        print("-" * 68)
        for word, tags in ambiguous:
            ordered = sorted(tags, key=lambda t: tag_precedence.get(t, 999))
            print(f"  '{word}' → possible tags (by rules frequency): {', '.join(ordered)}")
        total_combos = 1
        for token in tokens:
            total_combos *= len(word_to_tags_multi.get(token, ['UNKNOWN']))
        print(f"\n  Total tag combinations to try: {total_combos}")
        print("=" * 68)
    else:
        print("\n  ✅ No ambiguous words — each word has exactly one tag.")
        print("=" * 68)


def display_resolution_report(resolutions):
    """
    Shows how each ambiguous word's tag was resolved using
    the grammar rules and sentence context.
    """
    if not resolutions:
        return

    print("\n  🔍 CONTEXT-BASED TAG RESOLUTION (from rules file):")
    print("-" * 68)

    for r in resolutions:
        word     = r['word']
        selected = r['selected']
        scores   = r['scores']
        left     = r['left_ctx']
        right    = r['right_ctx']

        print(f"\n  Word: '{word}'")
        if left:
            print(f"  Left neighbour:  '{left[0]}' (tag: {left[1]})")
        if right:
            print(f"  Right neighbour: '{right[0]}' (tag: {right[1]})")
        print(f"  Rules file scores:")

        score_rows = sorted(scores.items(), key=lambda x: -x[1])
        for tag, score in score_rows:
            marker = " ← selected" if tag == selected else ""
            print(f"    {tag:30} score: {score}{marker}")

    print("=" * 68)


def display_best_parse(score, tagged_combo, tree):
    """Displays the best parse with explanation of which rules matched."""
    print("\n" + "=" * 68)
    print(f"  🏆 BEST PARSE  (Rule-Match Score: {score})")
    print("=" * 68)

    print("\n  Tags used for this parse:")
    tag_table = [[w, t, LABEL_MAP.get(t, t)] for w, t in tagged_combo]
    print(tabulate(tag_table, headers=["Word", "Tag", "Meaning"], tablefmt="simple"))

    print("\n  Grammar rules that matched:")
    print("-" * 68)
    matched = []
    for subtree in tree.subtrees():
        if subtree != tree and isinstance(subtree, nltk.Tree):
            words = " ".join(w for w, _ in subtree.leaves())
            tags  = " ".join(t for _, t in subtree.leaves())
            matched.append([subtree.label(), words, tags])
    if matched:
        print(tabulate(matched,
                       headers=["Phrase", "Words", "Tags matched"],
                       tablefmt="simple"))
    else:
        print("  (no phrase rules fired)")

    print(f"\n  🌳 BEST PARSE — Bracket Notation:")
    print("-" * 68)
    print(tree)

    print(f"\n  🌳 BEST PARSE — Visual Tree:")
    print("-" * 68)
    tree.pretty_print()
    print("=" * 68)
    tree.draw()


def display_alternative_parses(alternatives):
    """Displays all alternative parses with their scores."""
    if not alternatives:
        return

    print(f"\n  📋 ALTERNATIVE PARSES ({len(alternatives)} other valid combination(s)):")
    print("=" * 68)

    for i, (score, tagged_combo, tree) in enumerate(alternatives, 2):
        print(f"\n  — Alternative Parse {i}  (Score: {score})")
        print("-" * 68)
        tags_used = "  |  ".join(f"{w}→{t}" for w, t in tagged_combo)
        print(f"  Tags: {tags_used}")
        print(f"\n  Visual Tree:")
        tree.pretty_print()
        print("-" * 68)


def display_fallback_tree(tree):
    """Shown when no structured parse is found."""
    print("\n  ℹ️  No structured parse found across any tag combination.")
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
    print("    🐍 SETSWANA CONSTITUENCY PARSER")
    print("    Powered by NLTK + Definitions & Grammar Rules")
    print("    Rule-Guided Tag Resolution & Best Parse: ENABLED")
    print("=" * 68)

    # ── Load grammar rules ────────────────────────────────
    print("\n⏳ Loading grammar rules ...")
    grammar_string = load_rules(RULES_FILE)
    print(f"   ✅ Grammar rules loaded.")

    # ── Learn tag precedence FROM the rules file ──────────
    print("⏳ Learning tag precedence from rules file ...")
    tag_precedence, tag_freq = build_tag_precedence_from_rules(RULES_FILE)
    top5 = sorted(tag_freq.items(), key=lambda x: -x[1])[:5]
    print(f"   ✅ Precedence learned. Top 5 tags by rule frequency:")
    for tag, count in top5:
        print(f"      {tag:25} appears in {count} rules → rank {tag_precedence[tag]}")

    # ── Build rules dictionary for context resolution ─────
    print("⏳ Building rules index for context resolution ...")
    rules_dict = build_rules_dict(RULES_FILE)
    print(f"   ✅ {len(rules_dict)} rule groups indexed.")

    # ── Load single-tag dict (for display) ────────────────
    print("⏳ Loading definitions (single-tag) ...")
    word_to_tag = load_definitions(DEFINITIONS_FILE)
    print(f"   ✅ {len(word_to_tag)} words loaded.")

    # ── Load multi-tag dict with rules-derived precedence ─
    print("⏳ Loading definitions (multi-tag) ...")
    word_to_tags_multi = load_definitions_multi(DEFINITIONS_FILE, tag_precedence)
    ambiguous_count = sum(
        1 for tags in word_to_tags_multi.values() if len(tags) > 1
    )
    print(f"   ✅ {len(word_to_tags_multi)} words loaded.")
    print(f"   🔀 {ambiguous_count} words have multiple possible tags.")

    print("\nType a Setswana sentence and press Enter.")
    print("Type 'exit' to quit.\n")

    while True:
        sentence = input("👉 Sentence: ").strip()

        if not sentence:
            continue
        if sentence.lower() == 'exit':
            print("\nTsamaya sentle! 👋\n")
            break

        # ── 1. Tag with primary tags (for display) ────────
        tagged = tag_sentence(sentence, word_to_tag)

        # ── 2. Show tagging table with alt tags ───────────
        display_tagging(tagged, sentence, word_to_tags_multi)

        # ── 3. Show constituency breakdown ────────────────
        display_constituents(tagged)

        # ── 4. Report ambiguous words ─────────────────────
        display_ambiguity_report(sentence, word_to_tags_multi, tag_precedence)

        # ── 5. Resolve ambiguous tags using rules context ─
        resolved, resolutions = resolve_sentence_tags(
            sentence, word_to_tag, word_to_tags_multi, rules_dict
        )

        # ── 6. Show how each ambiguous word was resolved ──
        display_resolution_report(resolutions)

        # ── 7. Try all combinations, score and rank ───────
        print("\n⏳ Parsing all tag combinations ...")
        valid_parses = parse_with_ambiguity(
            sentence, word_to_tags_multi, grammar_string
        )

        if not valid_parses:
            fallback = parse_sentence(resolved, grammar_string)
            display_fallback_tree(fallback)
        else:
            print(f"   ✅ Found {len(valid_parses)} structured parse(s).\n")
            best_score, best_combo, best_tree = valid_parses[0]
            display_best_parse(best_score, best_combo, best_tree)
            display_alternative_parses(valid_parses[1:])

        print()


if __name__ == '__main__':
    main()
