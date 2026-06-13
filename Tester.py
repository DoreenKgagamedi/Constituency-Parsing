"""
============================================================
  SETSWANA CONSTITUENCY PARSER — TEST SUITE
  Tests all 5 core functions of the new parser.
  Run: python Tester.py
============================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from setswana_parser import (
    load_definitions_multi,
    load_grammar_rules,
    check_word_tags,
    generate_tag_sequences,
    parse_sequence,
)
from tabulate import tabulate
from collections import Counter
import nltk

# ─────────────────────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_FILE = os.path.join(BASE_DIR, 'definitions.txt')
RULES_FILE       = os.path.join(BASE_DIR, 'Parsing Regex.txt')

# ─────────────────────────────────────────────────────────
# COLOURS & HELPERS
# ─────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

results = {"passed": 0, "failed": 0, "warnings": 0}

def PASS(name, msg=""):
    results["passed"] += 1
    print(f"  {GREEN}✅ PASS{RESET} — {name}" + (f": {msg}" if msg else ""))

def FAIL(name, msg=""):
    results["failed"] += 1
    print(f"  {RED}❌ FAIL{RESET} — {name}" + (f": {msg}" if msg else ""))

def WARN(name, msg=""):
    results["warnings"] += 1
    print(f"  {YELLOW}⚠️  WARN{RESET} — {name}" + (f": {msg}" if msg else ""))

def section(title):
    print(f"\n{BOLD}{BLUE}{'─'*65}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'─'*65}{RESET}")


# ─────────────────────────────────────────────────────────
# LOAD FILES
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}{'='*65}{RESET}")
print(f"{BOLD}   🐍 SETSWANA PARSER — TEST SUITE{RESET}")
print(f"{BOLD}{'='*65}{RESET}")
print("\n⏳ Loading files...\n")

word_to_tags   = load_definitions_multi(DEFINITIONS_FILE)
grammar_string = load_grammar_rules(RULES_FILE)

print(f"   definitions.txt → {len(word_to_tags)} words loaded")
print(f"   rules file      → grammar loaded ({len(grammar_string)} chars)")


# ══════════════════════════════════════════════════════════
# BLOCK 1: FUNCTION 1 — load_definitions_multi()
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 1: load_definitions_multi()")

# 1.1 — Dictionary is not empty
PASS("Dictionary loaded", f"{len(word_to_tags)} words") \
    if word_to_tags else FAIL("Dictionary loaded", "Empty!")

# 1.2 — Each value is a list
sample_values = list(word_to_tags.values())[:5]
all_lists = all(isinstance(v, list) for v in sample_values)
PASS("All values are lists", f"e.g. {sample_values[0]}") \
    if all_lists else FAIL("Values are lists", str(sample_values))

# 1.3 — Single-tag words have a one-item list
single_tag_words = {w: t for w, t in word_to_tags.items() if len(t) == 1}
PASS("Single-tag words stored as one-item lists",
     f"{len(single_tag_words)} words with one tag") \
    if single_tag_words else WARN("No single-tag words found")

# 1.4 — Multi-tag words exist
multi_tag_words = {w: t for w, t in word_to_tags.items() if len(t) > 1}
if multi_tag_words:
    PASS("Multi-tag words found", f"{len(multi_tag_words)} ambiguous words")
    sample_multi = list(multi_tag_words.items())[:3]
    for word, tags in sample_multi:
        print(f"       e.g. '{word}' → {tags}")
else:
    WARN("No multi-tag words found",
         "definitions.txt may have no overlapping words")

# 1.5 — Key words are correctly loaded
for word, expected_tags in [
    ('bana',    ['NN']),
    ('kgosi',   ['NN']),
    ('tsamaya', ['VRB']),
    ('ke',      ['L28']),
    ('le',      ['CC6']),
]:
    actual = word_to_tags.get(word, ['NOT FOUND'])
    if set(expected_tags).issubset(set(actual)):
        PASS(f"'{word}' in dictionary", f"tags: {actual}")
    else:
        FAIL(f"'{word}' in dictionary",
             f"Expected {expected_tags}, got {actual}")

# 1.6 — "bone" has multiple tags (VRB and leemedi)
bone_tags = word_to_tags.get('bone', [])
if 'VRB' in bone_tags and 'leemedi' in bone_tags:
    PASS("'bone' has both VRB and leemedi tags", f"tags: {bone_tags}")
elif len(bone_tags) > 1:
    PASS("'bone' has multiple tags", f"tags: {bone_tags}")
else:
    WARN("'bone' ambiguity check",
         f"Expected VRB+leemedi, got: {bone_tags}")

# 1.7 — No duplicate tags per word
dupes = {w: t for w, t in word_to_tags.items() if len(t) != len(set(t))}
PASS("No duplicate tags per word") \
    if not dupes else FAIL("Duplicate tags found", str(list(dupes.items())[:3]))

# 1.8 — Unknown word is not in dictionary
PASS("Unknown word not in dictionary") \
    if 'xyznotaword' not in word_to_tags \
    else FAIL("Unknown word should not be in dictionary")


# ══════════════════════════════════════════════════════════
# BLOCK 2: FUNCTION 2 — load_grammar_rules()
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 2: load_grammar_rules()")

# 2.1 — Grammar string is not empty
PASS("Grammar string loaded", f"{len(grammar_string)} characters") \
    if grammar_string and len(grammar_string) > 50 \
    else FAIL("Grammar string empty or too short")

# 2.2 — Grammar string contains rule group headers
import re
headers_found = re.findall(r'^\w+:', grammar_string, re.MULTILINE)
PASS("Rule group headers found", f"{len(headers_found)} groups") \
    if headers_found else FAIL("No rule headers found in grammar string")

# 2.3 — Grammar string contains valid patterns
patterns_found = re.findall(r'\{<[^}]+>\}', grammar_string)
PASS("Valid patterns found", f"{len(patterns_found)} patterns") \
    if patterns_found else FAIL("No valid patterns found")

# 2.4 — NLTK can parse the grammar string without errors
try:
    nltk.RegexpParser(grammar_string)
    PASS("NLTK accepts grammar string without errors")
except Exception as e:
    FAIL("NLTK grammar string error", str(e)[:80])

# 2.5 — Grammar has NP and VP rules
for group in ['NP', 'VP']:
    if f'{group}:' in grammar_string or f'{group} ' in grammar_string:
        PASS(f"Rule group '{group}' found in grammar")
    else:
        WARN(f"Rule group '{group}' not found",
             "May be named differently")


# ══════════════════════════════════════════════════════════
# BLOCK 3: FUNCTION 3 — check_word_tags()
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 3: check_word_tags()")

# 3.1 — Returns a list of dicts
result = check_word_tags("bana tsamaya", word_to_tags)
PASS("Returns list of dicts", f"{len(result)} entries") \
    if isinstance(result, list) and all(isinstance(r, dict) for r in result) \
    else FAIL("Return type", f"Got {type(result)}")

# 3.2 — Each dict has required keys
required_keys = {'word', 'tags', 'ambiguous'}
for entry in result:
    if not required_keys.issubset(entry.keys()):
        FAIL("Dict missing keys",
             f"Expected {required_keys}, got {set(entry.keys())}")
        break
else:
    PASS("All dicts have required keys", str(required_keys))

# 3.3 — Correct number of entries (one per word)
result3 = check_word_tags("bana tsamaya sentle", word_to_tags)
PASS("One entry per word", f"3 words → {len(result3)} entries") \
    if len(result3) == 3 else FAIL("Entry count", f"Expected 3, got {len(result3)}")

# 3.4 — Single-tag word is not flagged ambiguous
bana_entry = check_word_tags("bana", word_to_tags)[0]
PASS("Single-tag word not flagged ambiguous",
     f"'bana' ambiguous={bana_entry['ambiguous']}") \
    if not bana_entry['ambiguous'] \
    else FAIL("Single-tag word falsely flagged ambiguous")

# 3.5 — Multi-tag word IS flagged ambiguous
bone_entry = check_word_tags("bone", word_to_tags)[0]
if bone_entry['ambiguous']:
    PASS("Multi-tag word correctly flagged ambiguous",
         f"'bone' tags: {bone_entry['tags']}")
else:
    WARN("'bone' not flagged ambiguous",
         f"tags found: {bone_entry['tags']}")

# 3.6 — Unknown word gets ['UNKNOWN']
unknown_entry = check_word_tags("xyznotaword", word_to_tags)[0]
PASS("Unknown word gets ['UNKNOWN'] tag",
     f"tags: {unknown_entry['tags']}") \
    if unknown_entry['tags'] == ['UNKNOWN'] \
    else FAIL("Unknown word tags", f"Got {unknown_entry['tags']}")

# 3.7 — Case insensitive (uppercase input)
upper_result = check_word_tags("BANA", word_to_tags)[0]
PASS("Uppercase input lowercased", f"BANA → tags: {upper_result['tags']}") \
    if upper_result['tags'] != ['UNKNOWN'] \
    else FAIL("Uppercase not lowercased", "Got UNKNOWN")

# 3.8 — The example sentence from the spec
spec_sentence  = "mosadi wa kgosi o bone kotsi"
spec_result    = check_word_tags(spec_sentence, word_to_tags)
ambiguous_spec = [e['word'] for e in spec_result if e['ambiguous']]
print(f"\n  Spec sentence check: '{spec_sentence}'")
for e in spec_result:
    marker = " ← ambiguous" if e['ambiguous'] else ""
    print(f"    '{e['word']}' → {e['tags']}{marker}")
PASS("Spec sentence processed", f"Ambiguous: {ambiguous_spec}")


# ══════════════════════════════════════════════════════════
# BLOCK 4: FUNCTION 4 — generate_tag_sequences()
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 4: generate_tag_sequences()")

# 4.1 — No ambiguous words → exactly 1 sequence
no_ambig = check_word_tags("bana tsamaya", word_to_tags)
seqs_1   = generate_tag_sequences(no_ambig)
PASS("No ambiguity → 1 sequence", f"{len(seqs_1)} sequence(s)") \
    if len(seqs_1) == 1 else FAIL("Expected 1 sequence", f"Got {len(seqs_1)}")

# 4.2 — One word with 2 tags → exactly 2 sequences
# Build a manual word_tag_info with one ambiguous word
manual_info = [
    {'word': 'kgosi', 'tags': ['NN'],          'ambiguous': False},
    {'word': 'bone',  'tags': ['VRB','leemedi'],'ambiguous': True},
    {'word': 'kotsi', 'tags': ['NN'],           'ambiguous': False},
]
seqs_2 = generate_tag_sequences(manual_info)
PASS("1 ambiguous word (2 tags) → 2 sequences",
     f"{len(seqs_2)} sequence(s)") \
    if len(seqs_2) == 2 else FAIL("Expected 2 sequences", f"Got {len(seqs_2)}")

# 4.3 — Two words each with 2 tags → 4 sequences (2×2)
manual_info_2 = [
    {'word': 'a', 'tags': ['CC7','L07'], 'ambiguous': True},
    {'word': 'b', 'tags': ['NN','VRB'],  'ambiguous': True},
]
seqs_4 = generate_tag_sequences(manual_info_2)
PASS("2 ambiguous words (2 tags each) → 4 sequences",
     f"{len(seqs_4)} sequence(s)") \
    if len(seqs_4) == 4 else FAIL("Expected 4 sequences", f"Got {len(seqs_4)}")

# 4.4 — Each sequence is the correct length
word_count = len(manual_info)
for i, seq in enumerate(seqs_2):
    if len(seq) != word_count:
        FAIL(f"Sequence {i+1} wrong length",
             f"Expected {word_count}, got {len(seq)}")
        break
else:
    PASS("All sequences have correct length",
         f"{word_count} words per sequence")

# 4.5 — Each entry in sequence is a (word, tag) tuple
for w, t in seqs_2[0]:
    if not (isinstance(w, str) and isinstance(t, str)):
        FAIL("Sequence entries are (str,str) tuples",
             f"Got ({type(w)},{type(t)})")
        break
else:
    PASS("Sequence entries are (word, tag) string pairs")

# 4.6 — No duplicate sequences
seq_strs = [str(s) for s in seqs_2]
PASS("No duplicate sequences generated") \
    if len(seq_strs) == len(set(seq_strs)) \
    else FAIL("Duplicate sequences found")

# 4.7 — Spec sentence sequences
spec_info  = check_word_tags("mosadi wa kgosi o bone kotsi", word_to_tags)
spec_seqs  = generate_tag_sequences(spec_info)
total_exp  = 1
for e in spec_info:
    total_exp *= len(e['tags'])
PASS("Spec sentence generates correct number of sequences",
     f"Expected {total_exp}, got {len(spec_seqs)}") \
    if len(spec_seqs) == total_exp \
    else FAIL("Spec sequence count",
              f"Expected {total_exp}, got {len(spec_seqs)}")

print(f"\n  All {len(spec_seqs)} sequence(s) for spec sentence:")
for i, seq in enumerate(spec_seqs, 1):
    tag_line = " ".join(t for _, t in seq)
    print(f"    Sequence {i}: {tag_line}")


# ══════════════════════════════════════════════════════════
# BLOCK 5: FUNCTION 5 — parse_sequence()
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 5: parse_sequence()")

# 5.1 — Returns an nltk.Tree or None (never crashes)
test_seq = [('bana', 'NN'), ('tsamaya', 'VRB')]
try:
    tree = parse_sequence(test_seq, grammar_string)
    PASS("parse_sequence doesn't crash",
         f"Returned: {type(tree).__name__}")
except Exception as e:
    FAIL("parse_sequence crashed", str(e))

# 5.2 — Returns nltk.Tree type on valid input
test_seq2 = check_word_tags("bana tsamaya", word_to_tags)
seqs2     = generate_tag_sequences(test_seq2)
tree2     = parse_sequence(seqs2[0], grammar_string)
PASS("Returns nltk.Tree", f"Type: {type(tree2).__name__}") \
    if isinstance(tree2, nltk.Tree) \
    else FAIL("Return type", f"Got {type(tree2)}")

# 5.3 — Tree label is 'S' (sentence root)
PASS("Tree root label is 'S'", f"Label: {tree2.label()}") \
    if tree2 and tree2.label() == 'S' \
    else FAIL("Tree root label", f"Got '{tree2.label() if tree2 else None}'")

# 5.4 — Tree leaves match input words
if tree2:
    input_words = [w for w, _ in seqs2[0]]
    tree_words  = [w for w, _ in tree2.leaves()]
    PASS("Tree leaves match input words",
         f"Input: {input_words}, Leaves: {tree_words}") \
        if input_words == tree_words \
        else FAIL("Tree leaves mismatch",
                  f"Input: {input_words}, Leaves: {tree_words}")

# 5.5 — All sequences from spec sentence parse without crashing
spec_info  = check_word_tags("mosadi wa kgosi o bone kotsi", word_to_tags)
spec_seqs  = generate_tag_sequences(spec_info)
crash_count = 0
none_count  = 0
tree_count  = 0
for seq in spec_seqs:
    try:
        t = parse_sequence(seq, grammar_string)
        if t is None:
            none_count += 1
        else:
            tree_count += 1
    except Exception:
        crash_count += 1

PASS("Spec sentence sequences parse without crashing",
     f"Trees: {tree_count}, None: {none_count}, Crashes: {crash_count}") \
    if crash_count == 0 \
    else FAIL("Crashes during spec sentence parsing",
              f"{crash_count} crash(es)")

# 5.6 — Each sequence produces a different or same tree (both valid)
if len(spec_seqs) > 1:
    trees = [str(parse_sequence(s, grammar_string)) for s in spec_seqs]
    unique_trees = len(set(t for t in trees if t != 'None'))
    print(f"\n  Unique parse trees from spec sequences: {unique_trees}")
    PASS("Multiple sequences processed",
         f"{len(spec_seqs)} sequences → {unique_trees} unique tree(s)")


# ══════════════════════════════════════════════════════════
# BLOCK 6: EDGE CASES
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 6: Edge Cases")

# 6.1 — Empty grammar string → parse_sequence returns None
PASS("Empty grammar → None") \
    if parse_sequence([('bana','NN')], "") is None \
    else FAIL("Empty grammar should return None")

# 6.2 — Single word sentence
single = check_word_tags("kgosi", word_to_tags)
seqs_s = generate_tag_sequences(single)
PASS("Single word → 1 sequence", f"{len(seqs_s)} sequence") \
    if len(seqs_s) == 1 else FAIL("Single word sequence count")

# 6.3 — All unknown words still generates a sequence
all_unk = check_word_tags("xyz abc def", word_to_tags)
seqs_u  = generate_tag_sequences(all_unk)
PASS("All-unknown sentence generates 1 sequence",
     f"{len(seqs_u)} sequence") \
    if len(seqs_u) == 1 else FAIL("All-unknown sequence count")

# 6.4 — Tags field is always a list, never a string
for word, info in list(word_to_tags.items())[:20]:
    if not isinstance(info, list):
        FAIL("Tags not stored as list", f"'{word}' → {type(info)}")
        break
else:
    PASS("Tags always stored as lists for first 20 words")

# 6.5 — Whitespace-only input handled
ws_result = check_word_tags("   bana   kgosi   ", word_to_tags)
PASS("Extra whitespace handled", f"{len(ws_result)} words found") \
    if len(ws_result) == 2 else FAIL("Whitespace handling", f"Got {len(ws_result)}")


# ══════════════════════════════════════════════════════════
# BLOCK 7: COVERAGE REPORT
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 7: Dictionary Coverage Report")

# Flatten all tags for counting
all_tags    = [tag for tags in word_to_tags.values() for tag in tags]
tag_counts  = Counter(all_tags)
multi_words = {w: t for w, t in word_to_tags.items() if len(t) > 1}

coverage = []
for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    ambig_count = sum(1 for w, tags in word_to_tags.items()
                      if tag in tags and len(tags) > 1)
    coverage.append([tag, count, ambig_count, "█" * min(count // 2, 30)])

print(tabulate(
    coverage,
    headers=["Tag", "Words", "Ambiguous words", "Visual"],
    tablefmt="fancy_grid"
))

total      = len(word_to_tags)
total_tags = len(all_tags)
total_amb  = len(multi_words)

print(f"\n  Total unique words     : {total}")
print(f"  Total tag assignments  : {total_tags}")
print(f"  Ambiguous words        : {total_amb} ({round(total_amb/total*100,1)}% of vocab)")
print(f"  Max tags on one word   : {max(len(t) for t in word_to_tags.values())}")

if total_amb > 0:
    print(f"\n  Sample ambiguous words:")
    for word, tags in list(multi_words.items())[:8]:
        print(f"    '{word}' → {tags}")

PASS("Coverage report generated", f"{total} words, {total_amb} ambiguous") \
    if total > 0 else FAIL("No words in dictionary")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*65}{RESET}")
print(f"{BOLD}    TEST RESULTS SUMMARY{RESET}")
print(f"{BOLD}{'='*65}{RESET}\n")

total_tests = results["passed"] + results["failed"] + results["warnings"]
pass_rate   = round(results["passed"] / total_tests * 100, 1) if total_tests else 0

print(tabulate([
    ["✅ Passed",    results["passed"],   f"{pass_rate}%"],
    ["❌ Failed",    results["failed"],   ""],
    ["⚠️  Warnings", results["warnings"], ""],
    ["📋 Total",     total_tests,         ""],
], headers=["Result", "Count", "Rate"], tablefmt="fancy_grid"))

print()
if results["failed"] == 0 and results["warnings"] == 0:
    print(f"{GREEN}{BOLD}   ✅ ALL TESTS PASSED!{RESET}\n")
elif results["failed"] == 0:
    print(f"{YELLOW}{BOLD}   All tests passed with warnings to review.{RESET}\n")
elif results["failed"] <= 3:
    print(f"{YELLOW}{BOLD}   Mostly passing — review {results['failed']} failure(s).{RESET}\n")
else:
    print(f"{RED}{BOLD}   Several failures — review errors above.{RESET}\n")

print(f"{BOLD}{'='*65}{RESET}\n")
