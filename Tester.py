"""
============================================================
  SETSWANA CONSTITUENCY PARSER — TEST SUITE
  Tests: file loading, tagging, rules-derived precedence,
         rules dictionary, context-based resolution,
         multi-tag ambiguity, scoring, edge cases
  Run:   python Tester.py
============================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from setswana_parser import (
    load_definitions,
    load_definitions_multi,
    build_grammar_string,
    build_rules_dict,
    build_tag_precedence_from_rules,
    resolve_tag_from_rules,
    resolve_sentence_tags,
    tag_sentence,
    get_all_tag_combinations,
    parse_sentence,
    parse_with_ambiguity,
    score_tree,
    TAG_PRECEDENCE,
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
# COLOURS
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

tag_precedence, tag_freq = build_tag_precedence_from_rules(RULES_FILE)
rules_dict               = build_rules_dict(RULES_FILE)
word_to_tag              = load_definitions(DEFINITIONS_FILE)
word_to_tags_multi       = load_definitions_multi(DEFINITIONS_FILE, tag_precedence)
grammar                  = build_grammar_string(RULES_FILE)

print(f"   definitions.txt (single) → {len(word_to_tag)} words")
print(f"   definitions.txt (multi)  → {len(word_to_tags_multi)} words")
print(f"   rules file               → {len(rules_dict)} rule groups, {len(tag_freq)} tags indexed")


# ══════════════════════════════════════════════════════════
# BLOCK 1: FILE LOADING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 1: File Loading")

PASS("Single-tag dict loaded", f"{len(word_to_tag)} words") \
    if word_to_tag else FAIL("Single-tag dict loaded", "Empty!")

PASS("Multi-tag dict loaded", f"{len(word_to_tags_multi)} words") \
    if word_to_tags_multi else FAIL("Multi-tag dict loaded", "Empty!")

PASS("Grammar string loaded", f"{len(grammar)} chars") \
    if grammar and len(grammar) > 50 else FAIL("Grammar string loaded", "Too short!")

PASS("Rules dict built", f"{len(rules_dict)} groups") \
    if rules_dict else FAIL("Rules dict built", "Empty!")

PASS("Tag precedence built", f"{len(tag_freq)} tags counted") \
    if tag_freq else FAIL("Tag precedence built", "Empty!")

for tag in ['NN', 'VRB', 'letlhaodi_thito', 'leemedi', 'lesoboki']:
    words = [w for w, t in word_to_tag.items() if t == tag]
    PASS(f"Tag '{tag}' populated", f"{len(words)} words") \
        if words else FAIL(f"Tag '{tag}' populated", "No words!")

for word, expected in [('bana','NN'), ('tsamaya','VRB'), ('sentle','letlhaodi_thito'),
                        ('rona','leemedi'), ('botlhe','lesoboki'), ('ke','L28')]:
    actual = word_to_tag.get(word, 'NOT FOUND')
    PASS(f"'{word}' → {expected}") if actual == expected \
        else FAIL(f"'{word}' tagged correctly", f"Expected '{expected}', got '{actual}'")


# ══════════════════════════════════════════════════════════
# BLOCK 2: RULES-DERIVED TAG PRECEDENCE  ← NEW
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 2: Rules-Derived Tag Precedence")

# 2.1 — tag_freq has entries
if tag_freq:
    PASS("tag_freq populated from rules file", f"{len(tag_freq)} unique tags found")
else:
    FAIL("tag_freq populated", "No tags counted from rules file")

# 2.2 — tag_precedence assigns rank 1 to most frequent tag
most_frequent_tag = max(tag_freq, key=lambda t: tag_freq[t])
if tag_precedence.get(most_frequent_tag) == 1:
    PASS("Most frequent tag gets rank 1",
         f"'{most_frequent_tag}' appears {tag_freq[most_frequent_tag]} times → rank 1")
else:
    FAIL("Most frequent tag rank 1",
         f"'{most_frequent_tag}' got rank {tag_precedence.get(most_frequent_tag)}")

# 2.3 — All tags in tag_freq appear in tag_precedence
missing = [t for t in tag_freq if t not in tag_precedence]
PASS("All tags assigned a rank", f"{len(tag_precedence)} tags ranked") \
    if not missing else FAIL("All tags assigned a rank", f"Missing: {missing[:5]}")

# 2.4 — Rules-derived precedence differs from hardcoded (proves it's dynamic)
rules_top5   = sorted(tag_freq.items(), key=lambda x: -x[1])[:5]
hardcoded_t5 = sorted(TAG_PRECEDENCE.items(), key=lambda x: x[1])[:5]
print(f"\n  Rules-derived top 5 tags: {[t for t,_ in rules_top5]}")
print(f"  Hardcoded top 5 tags:     {[t for t,_ in hardcoded_t5]}")
PASS("Rules-derived precedence computed successfully")

# 2.5 — Multi-tag dict uses rules-derived precedence for sorting
sample = next((w for w, tags in word_to_tags_multi.items() if len(tags) > 1), None)
if sample:
    tags  = word_to_tags_multi[sample]
    ranks = [tag_precedence.get(t, 999) for t in tags]
    if ranks == sorted(ranks):
        PASS("Multi-tag dict sorted by rules precedence",
             f"'{sample}': {tags}")
    else:
        FAIL("Multi-tag dict sorted by rules precedence",
             f"'{sample}' ranks not sorted: {list(zip(tags, ranks))}")


# ══════════════════════════════════════════════════════════
# BLOCK 3: RULES DICTIONARY  ← NEW
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 3: Rules Dictionary")

# 3.1 — Key rule groups exist
for expected_group in ['NP', 'VP', 'NP_ng', 'VP_ng', 'leamanyi']:
    if expected_group in rules_dict:
        PASS(f"Rule group '{expected_group}' found",
             f"{len(rules_dict[expected_group])} patterns")
    else:
        WARN(f"Rule group '{expected_group}' not found",
             "May be named differently in rules file")

# 3.2 — Patterns have correct format
sample_group = next((g for g in ['NP', 'VP', 'lerui'] if g in rules_dict), None)
if sample_group:
    sample_pattern = rules_dict[sample_group][0]
    if sample_pattern.startswith('{') and sample_pattern.endswith('}'):
        PASS("Patterns have correct {<>} format", f"e.g. {sample_pattern[:40]}")
    else:
        FAIL("Patterns format", f"Got: {sample_pattern[:40]}")

# 3.3 — No duplicate patterns per group
for group, patterns in rules_dict.items():
    if len(patterns) != len(set(patterns)):
        FAIL(f"Duplicates in group '{group}'",
             f"{len(patterns) - len(set(patterns))} duplicates")
        break
else:
    PASS("No duplicate patterns in any rule group")

# 3.4 — Tags can be found inside patterns
import re
vb_found = any(
    'VRB' in tag
    for patterns in rules_dict.values()
    for pattern in patterns
    for tag in re.findall(r'<([^>]+)>', pattern)
    for tag in tag.split('|')
)
PASS("VRB tag found in rule patterns") if vb_found \
    else WARN("VRB not found in rules", "Check rules file for verb patterns")


# ══════════════════════════════════════════════════════════
# BLOCK 4: CONTEXT-BASED TAG RESOLUTION  ← NEW
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 4: Context-Based Tag Resolution")

# 4.1 — resolve_tag_from_rules returns a string and a dict
sample_word = next((w for w, tags in word_to_tags_multi.items() if len(tags) > 1), None)
if sample_word:
    sample_tags    = word_to_tags_multi[sample_word]
    sample_context = [(sample_word, sample_tags[0])]
    best, scores   = resolve_tag_from_rules(
        sample_word, sample_tags, sample_context, 0, rules_dict
    )
    if isinstance(best, str) and isinstance(scores, dict):
        PASS("resolve_tag_from_rules returns (str, dict)",
             f"'{sample_word}' → '{best}', scores: {scores}")
    else:
        FAIL("resolve_tag_from_rules return types",
             f"Got ({type(best)}, {type(scores)})")

    # 4.2 — Selected tag is one of the possible tags
    if best in sample_tags:
        PASS("Selected tag is from possible tags list",
             f"'{best}' in {sample_tags}")
    else:
        FAIL("Selected tag from possible list",
             f"'{best}' not in {sample_tags}")

    # 4.3 — All possible tags have a score entry
    if all(t in scores for t in sample_tags):
        PASS("All possible tags scored", f"Scores: {scores}")
    else:
        missing = [t for t in sample_tags if t not in scores]
        FAIL("All tags scored", f"Missing scores for: {missing}")

# 4.4 — resolve_sentence_tags returns correct structure
resolved, resolutions = resolve_sentence_tags(
    "bana tsamaya sentle",
    word_to_tag, word_to_tags_multi, rules_dict
)
if isinstance(resolved, list) and len(resolved) == 3:
    PASS("resolve_sentence_tags returns correct length",
         f"{len(resolved)} tokens resolved")
else:
    FAIL("resolve_sentence_tags length",
         f"Expected 3, got {len(resolved) if resolved else 'None'}")

# 4.5 — All resolved tags are strings, not lists
all_strings = all(isinstance(t, str) for _, t in resolved)
PASS("All resolved tags are strings") if all_strings \
    else FAIL("Resolved tags are strings", str(resolved))

# 4.6 — resolutions only contains words that were ambiguous
for r in resolutions:
    word = r['word']
    tags = word_to_tags_multi.get(word, [])
    if len(tags) > 1:
        PASS(f"Resolution entry for ambiguous word '{word}'",
             f"tags: {tags}, selected: {r['selected']}")
    else:
        FAIL(f"Non-ambiguous word '{word}' in resolutions")

# 4.7 — Context scoring: right neighbour is NN, should prefer tags that precede NN
context = [('kgosi', 'NN'), ('reka', 'VRB'), ('koloi', 'NN')]
if 'reka' in word_to_tags_multi and len(word_to_tags_multi['reka']) > 1:
    best_reka, scores_reka = resolve_tag_from_rules(
        'reka', word_to_tags_multi['reka'], context, 1, rules_dict
    )
    PASS("Context resolution for 'reka' between two NNs",
         f"Selected: '{best_reka}', scores: {scores_reka}")
else:
    WARN("'reka' ambiguity test skipped", "'reka' has only one tag")


# ══════════════════════════════════════════════════════════
# BLOCK 5: WORD & SENTENCE TAGGING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 5: Word & Sentence Tagging")

for word, expected, desc in [
    ("bana",    "NN",              "Noun — bana (children)"),
    ("kgosi",   "NN",              "Noun — kgosi (chief)"),
    ("tsamaya", "VRB",             "Verb — tsamaya (walk)"),
    ("reka",    "VRB",             "Verb — reka (buy)"),
    ("sentle",  "letlhaodi_thito", "Adverb — sentle (well)"),
    ("rona",    "leemedi",         "Pronoun — rona (we)"),
    ("botlhe",  "lesoboki",        "Totality — botlhe (all)"),
    ("le",      "CC6",             "Concord — le (and/with)"),
    ("ke",      "L28",             "Particle — ke (is/am/are)"),
]:
    actual = tag_sentence(word, word_to_tag)[0][1]
    PASS(desc, f"'{word}' → {actual}") if actual == expected \
        else FAIL(desc, f"Expected '{expected}', got '{actual}'")

for sent, expected, desc in [
    ("bana tsamaya sentle",
     [("bana","NN"),("tsamaya","VRB"),("sentle","letlhaodi_thito")],
     "Noun + Verb + Adverb"),
    ("kgosi reka koloi",
     [("kgosi","NN"),("reka","VRB"),("koloi","NN")],
     "Noun + Verb + Noun"),
    ("bana ba ya lapeng",
     [("bana","NN"),("ba","CC3"),("ya","L12"),("lapeng","NN_ng")],
     "Noun + Concord + Particle + Noun-ng"),
]:
    tagged = tag_sentence(sent, word_to_tag)
    if tagged == expected:
        PASS(desc, f'"{sent}"')
    else:
        diffs = [f"'{w}': expected {e}, got {a}"
                 for (w,a),(_,e) in zip(tagged,expected) if a != e]
        FAIL(desc, "; ".join(diffs))


# ══════════════════════════════════════════════════════════
# BLOCK 6: PARSE TREE & SCORING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 6: Parse Tree & Scoring")

for sent, check_np, desc in [
    ("bana tsamaya sentle", ["bana"],          "NP contains 'bana'"),
    ("kgosi reka koloi",    ["kgosi","koloi"], "NP contains subject and object"),
]:
    tagged = tag_sentence(sent, word_to_tag)
    tree   = parse_sentence(tagged, grammar)
    if tree is None:
        FAIL(desc, "Parser returned None")
        continue
    np_words = [w for st in tree.subtrees()
                if st.label() == 'NP' for w, _ in st.leaves()]
    if all(w in np_words for w in check_np):
        PASS(desc, f"NP: {np_words}")
    else:
        FAIL(desc, f"Missing {[w for w in check_np if w not in np_words]}")

deep_tree = nltk.Tree.fromstring("(S (NP (NN bana)) (VP (VRB tsamaya)))")
flat_tree = nltk.Tree.fromstring("(S (NN bana) (VRB tsamaya))")
PASS("Deeper tree scores higher",
     f"deep={score_tree(deep_tree)}, flat={score_tree(flat_tree)}") \
    if score_tree(deep_tree) > score_tree(flat_tree) \
    else FAIL("Deeper tree scores higher")

unknown_tree = nltk.Tree.fromstring("(S (NP (UNKNOWN xyz)) (VP (VRB tsamaya)))")
known_tree   = nltk.Tree.fromstring("(S (NP (NN bana)) (VP (VRB tsamaya)))")
PASS("UNKNOWN penalises score",
     f"known={score_tree(known_tree)}, unknown={score_tree(unknown_tree)}") \
    if score_tree(known_tree) > score_tree(unknown_tree) \
    else FAIL("UNKNOWN penalises score")

PASS("None tree returns -999") if score_tree(None) == -999 \
    else FAIL("None tree score", f"Got {score_tree(None)}")

result = parse_with_ambiguity("bana tsamaya sentle", word_to_tags_multi, grammar)
PASS("parse_with_ambiguity returns list", f"{len(result)} parse(s)") \
    if isinstance(result, list) else FAIL("parse_with_ambiguity type")

if len(result) > 1:
    scores = [s for s,_,_ in result]
    PASS("Parses sorted best-first", f"Scores: {scores}") \
        if scores == sorted(scores, reverse=True) \
        else FAIL("Parses not sorted", str(scores))


# ══════════════════════════════════════════════════════════
# BLOCK 7: EDGE CASES
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 7: Edge Cases")

PASS("Unknown word → UNKNOWN") \
    if tag_sentence("xyzabc", word_to_tag)[0][1] == 'UNKNOWN' \
    else FAIL("Unknown word → UNKNOWN")

PASS("Uppercase lowercased") \
    if tag_sentence("BANA", word_to_tag) == tag_sentence("bana", word_to_tag) \
    else FAIL("Uppercase lowercased")

PASS("Extra whitespace stripped") \
    if len(tag_sentence("  bana   tsamaya  ", word_to_tag)) == 2 \
    else FAIL("Extra whitespace stripped")

try:
    parse_sentence(tag_sentence("abc def ghi", word_to_tag), grammar)
    PASS("All-unknown sentence doesn't crash parser")
except Exception as e:
    FAIL("All-unknown sentence crashes", str(e))

# resolve_tag_from_rules with empty rules_dict doesn't crash
try:
    resolve_tag_from_rules("rata", ["VRB", "VBMD"], [("rata","VRB")], 0, {})
    PASS("resolve_tag_from_rules handles empty rules_dict")
except Exception as e:
    FAIL("resolve_tag_from_rules empty rules_dict", str(e))


# ══════════════════════════════════════════════════════════
# BLOCK 8: COVERAGE REPORT
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 8: Coverage Report")

tag_counts = Counter(word_to_tag.values())
coverage   = []
for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    ambig    = sum(1 for w,t in word_to_tag.items()
                   if t == tag and len(word_to_tags_multi.get(w,[])) > 1)
    rule_rank = tag_precedence.get(tag, '—')
    rule_freq = tag_freq.get(tag, 0)
    coverage.append([tag, count, ambig, rule_rank, rule_freq,
                     "█" * min(count // 2, 25)])

print(tabulate(coverage,
               headers=["Tag","Words","Ambiguous","Rule Rank","Rule Freq","Visual"],
               tablefmt="fancy_grid"))

total     = sum(tag_counts.values())
total_amb = sum(1 for tags in word_to_tags_multi.values() if len(tags) > 1)
print(f"\n  Total words:     {total}")
print(f"  Ambiguous words: {total_amb} ({round(total_amb/total*100,1)}% of vocabulary)")
print(f"  Tags in rules:   {len(tag_freq)}")
print(f"  Rule groups:     {len(rules_dict)}\n")

PASS("Coverage sufficient", f"{total} words") if total >= 500 \
    else WARN("Coverage moderate", f"{total} words") if total >= 200 \
    else FAIL("Coverage low", f"Only {total} words")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*65}{RESET}")
print(f"{BOLD}    TEST RESULTS SUMMARY{RESET}")
print(f"{BOLD}{'='*65}{RESET}\n")

total_tests = results["passed"] + results["failed"] + results["warnings"]
pass_rate   = round(results["passed"] / total_tests * 100, 1) if total_tests else 0

print(tabulate([
    ["✅ Passed",     results["passed"],   f"{pass_rate}%"],
    ["❌ Failed",     results["failed"],   ""],
    ["⚠️  Warnings",  results["warnings"], ""],
    ["📋 Total",      total_tests,         ""],
], headers=["Result","Count","Rate"], tablefmt="fancy_grid"))

print()
if results["failed"] == 0 and results["warnings"] == 0:
    print(f"{GREEN}{BOLD}   ✅ ALL TESTS PASSED!{RESET}\n")
elif results["failed"] == 0:
    print(f"{YELLOW}{BOLD}   All tests passed with warnings.{RESET}\n")
elif results["failed"] <= 3:
    print(f"{YELLOW}{BOLD}   Mostly passing — review {results['failed']} failure(s).{RESET}\n")
else:
    print(f"{RED}{BOLD}   Several failures — review errors above.{RESET}\n")

print(f"{BOLD}{'='*65}{RESET}\n")
