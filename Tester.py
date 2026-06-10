"""
============================================================
  SETSWANA CONSTITUENCY PARSER — TEST SUITE
  Tests: file loading, tagging, multi-tag ambiguity,
         scoring, best parse selection, edge cases
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
    tag_sentence,
    get_all_tag_combinations,
    parse_sentence,
    parse_with_ambiguity,
    score_tree,
    TAG_PRECEDENCE,
)
from tabulate import tabulate
from collections import Counter

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

# ─────────────────────────────────────────────────────────
# TEST COUNTER
# ─────────────────────────────────────────────────────────
results = {"passed": 0, "failed": 0, "warnings": 0}

def PASS(name, msg=""):
    results["passed"] += 1
    print(f"  {GREEN} PASS{RESET} — {name}" + (f": {msg}" if msg else ""))

def FAIL(name, msg=""):
    results["failed"] += 1
    print(f"  {RED} FAIL{RESET} — {name}" + (f": {msg}" if msg else ""))

def WARN(name, msg=""):
    results["warnings"] += 1
    print(f"  {YELLOW}  WARN{RESET} — {name}" + (f": {msg}" if msg else ""))

def section(title):
    print(f"\n{BOLD}{BLUE}{'─'*65}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'─'*65}{RESET}")


# ─────────────────────────────────────────────────────────
# LOAD FILES
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}{'='*65}{RESET}")
print(f"{BOLD}  SETSWANA PARSER — TEST SUITE{RESET}")
print(f"{BOLD}{'='*65}{RESET}")
print("\n Loading files...\n")

word_to_tag        = load_definitions(DEFINITIONS_FILE)
word_to_tags_multi = load_definitions_multi(DEFINITIONS_FILE)
grammar            = build_grammar_string(RULES_FILE)

print(f"   definitions.txt (single) → {len(word_to_tag)} words")
print(f"   definitions.txt (multi)  → {len(word_to_tags_multi)} words")
print(f"   rules file               → grammar loaded")


# ══════════════════════════════════════════════════════════
# BLOCK 1: FILE LOADING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 1: File Loading")

if len(word_to_tag) > 0:
    PASS("Single-tag definitions loaded", f"{len(word_to_tag)} words")
else:
    FAIL("Single-tag definitions loaded", "No words loaded!")

if len(word_to_tags_multi) > 0:
    PASS("Multi-tag definitions loaded", f"{len(word_to_tags_multi)} words")
else:
    FAIL("Multi-tag definitions loaded", "No words loaded!")

if grammar and len(grammar) > 50:
    PASS("Rules file loaded", f"{len(grammar)} characters")
else:
    FAIL("Rules file loaded", "Grammar too short or empty!")

for tag in ['NN', 'VRB', 'letlhaodi_thito', 'leemedi', 'lesoboki', 'lebadi_thito']:
    words = [w for w, t in word_to_tag.items() if t == tag]
    if words:
        PASS(f"Tag '{tag}' populated", f"{len(words)} words")
    else:
        FAIL(f"Tag '{tag}' populated", "No words found!")

for word, expected in [('bana','NN'), ('tsamaya','VRB'), ('sentle','letlhaodi_thito'),
                        ('rona','leemedi'), ('botlhe','lesoboki'), ('ke','L28')]:
    actual = word_to_tag.get(word, 'NOT FOUND')
    if actual == expected:
        PASS(f"'{word}' → {expected}")
    else:
        FAIL(f"'{word}' tagged correctly", f"Expected '{expected}', got '{actual}'")


# ══════════════════════════════════════════════════════════
# BLOCK 2: WORD TAGGING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 2: Word Tagging")

tagging_tests = [
    ("bana",    "NN",               "Noun — bana (children)"),
    ("kgosi",   "NN",               "Noun — kgosi (chief/king)"),
    ("koloi",   "NN",               "Noun — koloi (car)"),
    ("sekolo",  "NN",               "Noun — sekolo (school)"),
    ("madi",    "NN",               "Noun — madi (money)"),
    ("tsamaya", "VRB",              "Verb — tsamaya (walk/go)"),
    ("reka",    "VRB",              "Verb — reka (buy)"),
    ("rata",    "VRB",              "Verb — rata (love/like)"),
    ("lwala",   "VRB",              "Verb — lwala (be sick)"),
    ("sentle",  "letlhaodi_thito",  "Adverb — sentle (well)"),
    ("thata",   "letlhaodi_tota",   "Intensifier — thata (very)"),
    ("rona",    "leemedi",          "Pronoun — rona (we/us)"),
    ("botlhe",  "lesoboki",         "Totality — botlhe (all)"),
    ("le",      "CC6",              "Concord — le (and/with)"),
    ("ke",      "L28",              "Particle — ke (is/am/are)"),
]

for word, expected, desc in tagging_tests:
    actual = tag_sentence(word, word_to_tag)[0][1]
    if actual == expected:
        PASS(desc, f"'{word}' → {actual}")
    else:
        FAIL(desc, f"Expected '{expected}', got '{actual}'")


# ══════════════════════════════════════════════════════════
# BLOCK 3: SENTENCE TAGGING
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 3: Full Sentence Tagging")

sentence_tests = [
    ("bana tsamaya sentle",
     [("bana","NN"),("tsamaya","VRB"),("sentle","letlhaodi_thito")],
     "Noun + Verb + Adverb"),
    ("kgosi reka koloi",
     [("kgosi","NN"),("reka","VRB"),("koloi","NN")],
     "Noun + Verb + Noun"),
    ("bona lwala bolwetsi",
     [("bona","leemedi"),("lwala","VRB"),("bolwetsi","NN")],
     "Pronoun + Verb + Noun"),
    ("bana ba ya lapeng",
     [("bana","NN"),("ba","CC3"),("ya","L12"),("lapeng","NN_ng")],
     "Noun + Concord + Particle + Noun-ng"),
]

for sent, expected, desc in sentence_tests:
    tagged = tag_sentence(sent, word_to_tag)
    if tagged == expected:
        PASS(desc, f'"{sent}"')
    else:
        diffs = [f"'{w}': expected {e}, got {a}"
                 for (w,a),(_,e) in zip(tagged,expected) if a != e]
        FAIL(desc, "; ".join(diffs))


# ══════════════════════════════════════════════════════════
# BLOCK 4: PARSE TREE STRUCTURE
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 4: Parse Tree Structure")

parse_tests = [
    ("bana tsamaya sentle", ["bana"],            "NP contains 'bana'"),
    ("kgosi reka koloi",    ["kgosi","koloi"],   "NP contains subject and object"),
    ("kgosi duela madi",    ["kgosi","madi"],    "NP for subject and object"),
    ("koloi kgaoga",        ["koloi"],           "NP for single subject"),
]

for sent, check_np, desc in parse_tests:
    tagged = tag_sentence(sent, word_to_tag)
    tree   = parse_sentence(tagged, grammar)
    if tree is None:
        FAIL(desc, "Parser returned None")
        continue
    np_words = [w for st in tree.subtrees()
                if st.label() == 'NP'
                for w, _ in st.leaves()]
    if all(w in np_words for w in check_np):
        PASS(desc, f"NP words: {np_words}")
    else:
        missing = [w for w in check_np if w not in np_words]
        FAIL(desc, f"Missing: {missing}, Found: {np_words}")


# ══════════════════════════════════════════════════════════
# BLOCK 5: MULTI-TAG AMBIGUITY
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 5: Multi-Tag Ambiguity Resolution")

# 5.1 — Multi-tag dict has ambiguous words
ambiguous_words = {w: tags for w, tags in word_to_tags_multi.items() if len(tags) > 1}
if ambiguous_words:
    PASS("Ambiguous words found", f"{len(ambiguous_words)} words with multiple tags")
else:
    WARN("Ambiguous words", "No words with multiple tags found")

# 5.2 — Tags sorted by precedence
sample = next((w for w, tags in word_to_tags_multi.items() if len(tags) > 1), None)
if sample:
    tags = word_to_tags_multi[sample]
    ranks = [TAG_PRECEDENCE.get(t, 99) for t in tags]
    if ranks == sorted(ranks):
        PASS("Tags sorted by precedence", f"'{sample}': {tags}")
    else:
        FAIL("Tags sorted by precedence", f"'{sample}' not sorted: {tags}")

# 5.3 — Combination count correct
test_sent = "bana tsamaya"
combos = get_all_tag_combinations(test_sent, word_to_tags_multi)
expected = (len(word_to_tags_multi.get('bana',['UNKNOWN'])) *
            len(word_to_tags_multi.get('tsamaya',['UNKNOWN'])))
if len(combos) == expected:
    PASS("Combination count correct", f"{len(combos)} combination(s)")
else:
    FAIL("Combination count correct", f"Expected {expected}, got {len(combos)}")

# 5.4 — parse_with_ambiguity returns sorted list
result = parse_with_ambiguity("bana tsamaya sentle", word_to_tags_multi, grammar)
if isinstance(result, list):
    PASS("parse_with_ambiguity returns list", f"{len(result)} parse(s)")
else:
    FAIL("parse_with_ambiguity returns list", f"Got {type(result)}")

# 5.5 — Results are sorted best-first (scores descending)
if len(result) > 1:
    scores = [s for s, _, _ in result]
    if scores == sorted(scores, reverse=True):
        PASS("Parses sorted best-first", f"Scores: {scores}")
    else:
        FAIL("Parses sorted best-first", f"Not sorted: {scores}")
else:
    PASS("Sort check skipped (0–1 parses)", "N/A")

# 5.6 — Best parse has highest score
if len(result) >= 2:
    best_score = result[0][0]
    other_scores = [s for s, _, _ in result[1:]]
    if all(best_score >= s for s in other_scores):
        PASS("Best parse has highest score", f"Best={best_score}, others={other_scores}")
    else:
        FAIL("Best parse has highest score", f"Best={best_score}, others={other_scores}")

# 5.7 — No duplicate trees
if result:
    tree_strs = [str(t) for _, _, t in result]
    if len(tree_strs) == len(set(tree_strs)):
        PASS("No duplicate trees", f"{len(result)} unique")
    else:
        FAIL("No duplicate trees", "Duplicates found!")


# ══════════════════════════════════════════════════════════
# BLOCK 6: SCORE FUNCTION
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 6: Tree Scoring")

import nltk

# 6.1 — Deeper tree scores higher than flat tree
deep_tree = nltk.Tree.fromstring("(S (NP (NN bana)) (VP (VRB tsamaya)))")
flat_tree = nltk.Tree.fromstring("(S (NN bana) (VRB tsamaya))")
deep_score = score_tree(deep_tree)
flat_score = score_tree(flat_tree)
if deep_score > flat_score:
    PASS("Deeper tree scores higher", f"deep={deep_score}, flat={flat_score}")
else:
    FAIL("Deeper tree scores higher", f"deep={deep_score}, flat={flat_score}")

# 6.2 — UNKNOWN tags reduce score
unknown_tree = nltk.Tree.fromstring("(S (NP (UNKNOWN xyz)) (VP (VRB tsamaya)))")
known_tree   = nltk.Tree.fromstring("(S (NP (NN bana)) (VP (VRB tsamaya)))")
if score_tree(known_tree) > score_tree(unknown_tree):
    PASS("UNKNOWN tags penalise score",
         f"known={score_tree(known_tree)}, unknown={score_tree(unknown_tree)}")
else:
    FAIL("UNKNOWN tags penalise score")

# 6.3 — None tree returns -999
if score_tree(None) == -999:
    PASS("None tree returns -999")
else:
    FAIL("None tree score", f"Got {score_tree(None)}")


# ══════════════════════════════════════════════════════════
# BLOCK 7: EDGE CASES
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 7: Edge Cases")

tagged = tag_sentence("xyzabc", word_to_tag)
PASS("Unknown word → UNKNOWN") if tagged[0][1] == 'UNKNOWN' \
    else FAIL("Unknown word → UNKNOWN", f"Got '{tagged[0][1]}'")

tagged = tag_sentence("bana xyzabc tsamaya", word_to_tag)
known   = [w for w, t in tagged if t != 'UNKNOWN']
unknown = [w for w, t in tagged if t == 'UNKNOWN']
if 'bana' in known and 'tsamaya' in known and 'xyzabc' in unknown:
    PASS("Mixed known/unknown handled", f"Known:{known}, Unknown:{unknown}")
else:
    FAIL("Mixed known/unknown handled", str(tagged))

if tag_sentence("BANA TSAMAYA", word_to_tag) == tag_sentence("bana tsamaya", word_to_tag):
    PASS("Uppercase lowercased correctly")
else:
    FAIL("Uppercase lowercased correctly")

if len(tag_sentence("  bana   tsamaya  ", word_to_tag)) == 2:
    PASS("Extra whitespace stripped")
else:
    FAIL("Extra whitespace stripped")

try:
    parse_sentence(tag_sentence("abc def ghi", word_to_tag), grammar)
    PASS("All-unknown sentence doesn't crash parser")
except Exception as e:
    FAIL("All-unknown sentence crashes parser", str(e))

cc_words = [w for w, t in word_to_tag.items() if t.startswith('CC') or t.startswith('C1')]
PASS("Concord (CC) words loaded", f"{len(cc_words)}") if cc_words \
    else FAIL("Concord (CC) words loaded", "None found!")

l_words = [w for w, t in word_to_tag.items() if t.startswith('L')]
PASS("Particle (L) words loaded", f"{len(l_words)}") if l_words \
    else FAIL("Particle (L) words loaded", "None found!")


# ══════════════════════════════════════════════════════════
# BLOCK 8: COVERAGE REPORT
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 8: Dictionary Coverage Report")

tag_counts = Counter(word_to_tag.values())
coverage   = []
for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    ambig = sum(1 for w, t in word_to_tag.items()
                if t == tag and len(word_to_tags_multi.get(w, [])) > 1)
    coverage.append([tag, count, ambig, "█" * min(count // 2, 30)])

print(tabulate(coverage,
               headers=["Tag", "Words", "Ambiguous", "Visual"],
               tablefmt="fancy_grid"))

total     = sum(tag_counts.values())
total_amb = sum(1 for tags in word_to_tags_multi.values() if len(tags) > 1)
print(f"\n  Total words:     {total}")
print(f"  Ambiguous words: {total_amb} ({round(total_amb/total*100,1)}% of vocabulary)\n")

if total >= 500:
    PASS("Coverage sufficient", f"{total} words, {len(tag_counts)} tags")
elif total >= 200:
    WARN("Coverage moderate", f"{total} words")
else:
    FAIL("Coverage low", f"Only {total} words")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*65}{RESET}")
print(f"{BOLD}    TEST RESULTS SUMMARY{RESET}")
print(f"{BOLD}{'='*65}{RESET}\n")

total_tests = results["passed"] + results["failed"] + results["warnings"]
pass_rate   = round(results["passed"] / total_tests * 100, 1) if total_tests else 0

print(tabulate([
    [" Passed",  results["passed"],   f"{pass_rate}%"],
    [" Failed",  results["failed"],   ""],
    ["  Warnings", results["warnings"], ""],
    [" Total",   total_tests,         ""],
], headers=["Result","Count","Rate"], tablefmt="fancy_grid"))

print()
if results["failed"] == 0 and results["warnings"] == 0:
    print(f"{GREEN}{BOLD}   ALL TESTS PASSED!{RESET}\n")
elif results["failed"] == 0:
    print(f"{YELLOW}{BOLD}   All tests passed with warnings.{RESET}\n")
elif results["failed"] <= 3:
    print(f"{YELLOW}{BOLD}   Mostly passing — review {results['failed']} failure(s).{RESET}\n")
else:
    print(f"{RED}{BOLD}   Several failures — review errors above.{RESET}\n")

print(f"{BOLD}{'='*65}{RESET}\n")
