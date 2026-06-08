
"""
============================================================
  SETSWANA CONSTITUENCY PARSER — TEST SUITE
  Tests: definitions loading, tagging, parsing, edge cases
  Run:   python test_setswana_parser.py
============================================================
"""
 
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from setswana_parser import (
    load_definitions,
    build_grammar_string,
    tag_sentence,
    parse_sentence
)
from tabulate import tabulate
 
# ─────────────────────────────────────────────────────────
# FILE PATHS — update these if your files are elsewhere
# ─────────────────────────────────────────────────────────
DEFINITIONS_FILE = "definitions.txt"
RULES_FILE       = "Parsing Regex.txt"
 
# ─────────────────────────────────────────────────────────
# COLOURS FOR TERMINAL OUTPUT
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
results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "details": []
}
 
def PASS(test_name, message=""):
    results["passed"] += 1
    results["details"].append((" PASS", test_name, message))
    print(f"  {GREEN} PASS{RESET} — {test_name}" + (f": {message}" if message else ""))
 
def FAIL(test_name, message=""):
    results["failed"] += 1
    results["details"].append((" FAIL", test_name, message))
    print(f"  {RED} FAIL{RESET} — {test_name}" + (f": {message}" if message else ""))
 
def WARN(test_name, message=""):
    results["warnings"] += 1
    results["details"].append(("  WARN", test_name, message))
    print(f"  {YELLOW}  WARN{RESET} — {test_name}" + (f": {message}" if message else ""))
 
def section(title):
    print(f"\n{BOLD}{BLUE}{'─'*60}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'─'*60}{RESET}")
 
 
# ─────────────────────────────────────────────────────────
# LOAD FILES ONCE FOR ALL TESTS
# ─────────────────────────────────────────────────────────
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}   🐍 SETSWANA PARSER — TEST SUITE{RESET}")
print(f"{BOLD}{'='*60}{RESET}")
print("\n⏳ Loading files...\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_FILE = os.path.join(BASE_DIR, 'definitions.txt')
RULES_FILE = os.path.join(BASE_DIR, 'Parsing Regex.txt')
 
word_to_tag = load_definitions(DEFINITIONS_FILE)
grammar     = build_grammar_string(RULES_FILE)
 
print(f"   definitions.txt  → {len(word_to_tag)} words loaded")
print(f"   rules file       → Grammar rules loaded")
 
 
# ══════════════════════════════════════════════════════════
# TEST BLOCK 1: FILE LOADING TESTS
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 1: File Loading")
 
# Test 1.1 — Definitions loaded
if len(word_to_tag) > 0:
    PASS("Definitions file loaded", f"{len(word_to_tag)} words found")
else:
    FAIL("Definitions file loaded", "No words were loaded!")
 
# Test 1.2 — Grammar rules loaded
if grammar and len(grammar) > 50:
    PASS("Rules file loaded", f"{len(grammar)} characters of grammar rules")
else:
    FAIL("Rules file loaded", "Grammar string is empty or too short!")
 
# Test 1.3 — Critical tags exist
critical_tags = ['NN', 'VRB', 'letlhaodi_thito', 'leemedi', 'lesoboki', 'lebadi_thito']
for tag in critical_tags:
    tag_words = [w for w, t in word_to_tag.items() if t == tag]
    if len(tag_words) > 0:
        PASS(f"Tag '{tag}' has words", f"{len(tag_words)} words")
    else:
        FAIL(f"Tag '{tag}' has words", "No words found for this tag!")
 
# Test 1.4 — Key words are in the dictionary
key_words = {
    'bana':    'NN',
    'kgosi':   'NN',
    'tsamaya': 'VRB',
    'reka':    'VRB',
    'sentle':  'letlhaodi_thito',
    'rona':    'leemedi',
    'botlhe':  'lesoboki',
}
for word, expected_tag in key_words.items():
    actual = word_to_tag.get(word, 'NOT FOUND')
    if actual == expected_tag:
        PASS(f"Word '{word}' tagged correctly", f"→ {actual}")
    else:
        FAIL(f"Word '{word}' tagged correctly", f"Expected '{expected_tag}', got '{actual}'")

# ══════════════════════════════════════════════════════════
# TEST BLOCK 2: TAGGING TESTS
# Tests that individual words get the RIGHT tag
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 2: Word Tagging")
 
tagging_tests = [
    # (word,        expected_tag,          description)
    ("bana",        "NN",                  "Noun — bana (children)"),
    ("kgosi",       "NN",                  "Noun — kgosi (chief/king)"),
    ("koloi",       "NN",                  "Noun — koloi (car)"),
    ("sekolo",      "NN",                  "Noun — sekolo (school)"),
    ("madi",        "NN",                  "Noun — madi (money)"),
    ("tsamaya",     "VRB",                 "Verb — tsamaya (walk/go)"),
    ("reka",        "VRB",                 "Verb — reka (buy)"),
    ("rata",        "VRB",                 "Verb — rata (love/like)"),
    ("lwala",       "VRB",                 "Verb — lwala (be sick)"),
    ("duela",       "VRB",                 "Verb — duela (pay)"),
    ("sentle",      "letlhaodi_thito",     "Adverb — sentle (well/nicely)"),
    ("bonako",      "letlhaodi_thito",     "Adverb — bonako (quickly/soon)"),
    ("gantsi",      "letlhaodi_thito",     "Adverb — gantsi (often)"),
    ("thata",       "letlhaodi_tota",      "Intensifier — thata (very/a lot)"),
    ("rona",        "leemedi",             "Pronoun — rona (we/us)"),
    ("ena",         "leemedi",             "Pronoun — ena (he/she/it)"),
    ("botlhe",      "lesoboki",            "Totality — botlhe (all/everyone)"),
    ("le",          "CC6",                 "Concord CC6 — le (and/with)"),
    ("ke",          "L28",                 "Particle L28 — ke (is/am/are)"),
]
 
for word, expected_tag, desc in tagging_tests:
    tagged = tag_sentence(word, word_to_tag)
    actual_tag = tagged[0][1] if tagged else "ERROR"
    if actual_tag == expected_tag:
        PASS(desc, f"'{word}' → {actual_tag}")
    else:
        FAIL(desc, f"'{word}' → expected '{expected_tag}', got '{actual_tag}'")

# ══════════════════════════════════════════════════════════
# TEST BLOCK 3: SENTENCE TAGGING TESTS
# Tests full sentences — checks every word gets tagged
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 3: Full Sentence Tagging")
 
sentence_tests = [
    {
        "sentence": "bana tsamaya sentle",
        "expected": [("bana","NN"), ("tsamaya","VRB"), ("sentle","letlhaodi_thito")],
        "desc":     "Noun + Verb + Adverb"
    },
    {
        "sentence": "kgosi reka koloi",
        "expected": [("kgosi","NN"), ("reka","VRB"), ("koloi","NN")],
        "desc":     "Noun + Verb + Noun"
    },
    {
        "sentence": "bana tsamaya bonako",
        "expected": [("bana","NN"), ("tsamaya","VRB"), ("bonako","letlhaodi_thito")],
        "desc":     "Noun + Verb + Speed Adverb"
    },
    {
        "sentence": "bona lwala bolwetsi",
        "expected": [("bona","leemedi"), ("lwala","VRB"), ("bolwetsi","NN")],
        "desc":     "Pronoun + Verb + Noun"
    },
    {
        "sentence": "kgosi duela madi",
        "expected": [("kgosi","NN"), ("duela","VRB"), ("madi","NN")],
        "desc":     "Noun + Verb + Noun (pay money)"
    },
    {
        "sentence": "bana tshameka gantsi",
        "expected": [("bana","NN"), ("tshameka","VRB"), ("gantsi","letlhaodi_thito")],
        "desc":     "Noun + Verb + Frequency Adverb"
    },
    {
        "sentence": "koloi kgaoga",
        "expected": [("koloi","NN"), ("kgaoga","VRB")],
        "desc":     "Noun + Verb (short sentence)"
    },
    {
        "sentence": "kgosi le bana tsamaya",
        "expected": [("kgosi","NN"), ("le","CC6"), ("bana","NN"), ("tsamaya","VRB")],
        "desc":     "Noun + Conjunction + Noun + Verb"
    },
    {
        "sentence": "ena reka dikoloi",
        "expected": [("ena","leemedi"), ("reka","VRB"), ("dikoloi","NN")],
        "desc":     "Pronoun + Verb + Noun"
    },
    {
        "sentence": "bana ba ya lapeng",
        "expected": [("bana","NN"), ("ba","CC3"), ("ya","L12"), ("lapeng","NN_ng")],
        "desc":     "Noun + Conjunction + Conjunction + Noun"
    }
]
 
for test in sentence_tests:
    tagged = tag_sentence(test["sentence"], word_to_tag)
    if tagged == test["expected"]:
        PASS(test["desc"], f'"{test["sentence"]}"')
    else:
        # Show which word(s) differed
        diffs = []
        for i, ((w, actual), (_, exp)) in enumerate(zip(tagged, test["expected"])):
            if actual != exp:
                diffs.append(f"'{w}': expected {exp}, got {actual}")
        FAIL(test["desc"], f'"{test["sentence"]}" — {"; ".join(diffs)}')


# ══════════════════════════════════════════════════════════
# TEST BLOCK 4: PARSE TREE TESTS
# Tests that NLTK builds a tree and NP chunks are correct
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 4: Parse Tree Structure")

parse_tests = [
    {
        "sentence":     "bana tsamaya sentle",
        "check_np":     ["bana"],
        "desc":         "NP chunk contains 'bana'"
    },
    {
        "sentence":     "kgosi reka koloi",
        "check_np":     ["kgosi", "koloi"],
        "desc":         "NP chunks contain 'kgosi' and 'koloi'"
    },
    {
        "sentence":     "kgosi duela madi",
        "check_np":     ["kgosi", "madi"],
        "desc":         "NP chunks for subject and object"
    },
    {
        "sentence":     "koloi kgaoga",
        "check_np":     ["koloi"],
        "desc":         "Single NP chunk for short sentence"
    },
    {
        "sentence":     "ena reka dikoloi",
        "check_np":     ["dikoloi"],
        "desc":         "NP chunk contains object noun"
    },
]

for test in parse_tests:
    tagged = tag_sentence(test["sentence"], word_to_tag)
    tree   = parse_sentence(tagged, grammar)

    if tree is None:
        FAIL(test["desc"], "Parser returned None — check grammar rules")
        continue

    # Extract words inside NP subtrees
    np_words = []
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            for word, tag in subtree.leaves():
                np_words.append(word)

    # Check all expected NP words are found
    all_found = all(w in np_words for w in test["check_np"])
    if all_found:
        PASS(test["desc"], f"NP words found: {np_words}")
    else:
        missing = [w for w in test["check_np"] if w not in np_words]
        FAIL(test["desc"], f"Missing from NP: {missing}. Found: {np_words}")

# ══════════════════════════════════════════════════════════
# TEST BLOCK 5: EDGE CASE TESTS
# Tests unusual or tricky inputs
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 5: Edge Cases")

# Test 5.1 — Unknown word gets UNKNOWN tag
tagged = tag_sentence("xyzabc", word_to_tag)
if tagged[0][1] == 'UNKNOWN':
    PASS("Unknown word gets UNKNOWN tag", "'xyzabc' → UNKNOWN")
else:
    FAIL("Unknown word gets UNKNOWN tag", f"Got '{tagged[0][1]}' instead")

# Test 5.2 — Mixed known/unknown sentence
tagged = tag_sentence("bana xyzabc tsamaya", word_to_tag)
known   = [w for w, t in tagged if t != 'UNKNOWN']
unknown = [w for w, t in tagged if t == 'UNKNOWN']
if 'bana' in known and 'tsamaya' in known and 'xyzabc' in unknown:
    PASS("Mixed known/unknown sentence handled", f"Known: {known}, Unknown: {unknown}")
else:
    FAIL("Mixed known/unknown sentence handled", f"Got: {tagged}")

# Test 5.3 — Uppercase input is handled (lowercasing)
tagged_upper = tag_sentence("BANA TSAMAYA", word_to_tag)
tagged_lower = tag_sentence("bana tsamaya", word_to_tag)
if tagged_upper == tagged_lower:
    PASS("Uppercase input lowercased correctly", "BANA → bana")
else:
    FAIL("Uppercase input lowercased correctly", f"Upper: {tagged_upper}, Lower: {tagged_lower}")

# Test 5.4 — Extra spaces handled
tagged_spaces = tag_sentence("  bana   tsamaya  ", word_to_tag)
if len(tagged_spaces) == 2:
    PASS("Extra whitespace stripped correctly", f"{tagged_spaces}")
else:
    FAIL("Extra whitespace stripped correctly", f"Got {len(tagged_spaces)} tokens: {tagged_spaces}")

# Test 5.5 — Empty-ish sentence (single word)
tagged_single = tag_sentence("kgosi", word_to_tag)
if len(tagged_single) == 1 and tagged_single[0] == ('kgosi', 'NN'):
    PASS("Single word sentence handled", "'kgosi' → NN")
else:
    FAIL("Single word sentence handled", f"Got: {tagged_single}")

# Test 5.6 — Parser does not crash on all-unknown sentence
try:
    tagged_unk = tag_sentence("abc def ghi", word_to_tag)
    tree = parse_sentence(tagged_unk, grammar)
    PASS("Parser handles all-unknown sentence without crashing")
except Exception as e:
    FAIL("Parser handles all-unknown sentence without crashing", str(e))

# Test 5.7 — Concord words (CC tags) are loaded
cc_words = [w for w, t in word_to_tag.items() if t.startswith('CC') or t.startswith('C1')]
if len(cc_words) > 0:
    PASS("Concord (CC) words loaded from definitions", f"{len(cc_words)} concord words")
else:
    FAIL("Concord (CC) words loaded from definitions", "No CC words found!")

# Test 5.8 — Particle words (L tags) are loaded
l_words = [w for w, t in word_to_tag.items() if t.startswith('L')]
if len(l_words) > 0:
    PASS("Particle (L) words loaded from definitions", f"{len(l_words)} particle words")
else:
    FAIL("Particle (L) words loaded from definitions", "No L-tag words found!")

# ══════════════════════════════════════════════════════════
# TEST BLOCK 6: COVERAGE REPORT
# Shows how many words exist per tag category
# ══════════════════════════════════════════════════════════
section("TEST BLOCK 6: Dictionary Coverage Report")

from collections import Counter
tag_counts = Counter(word_to_tag.values())

coverage_table = []
for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    coverage_table.append([tag, count, "█" * min(count // 2, 30)])

print(tabulate(
    coverage_table,
    headers=["Tag", "Word Count", "Visual"],
    tablefmt="fancy_grid"
))

total = sum(tag_counts.values())
if total >= 500:
    PASS("Dictionary has sufficient coverage", f"{total} total words across {len(tag_counts)} tags")
elif total >= 200:
    WARN("Dictionary coverage is moderate", f"{total} words — consider adding more")
else:
    FAIL("Dictionary coverage is low", f"Only {total} words found")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY REPORT
# ══════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}    TEST RESULTS SUMMARY{RESET}")
print(f"{BOLD}{'='*60}{RESET}\n")

total_tests = results["passed"] + results["failed"] + results["warnings"]
pass_rate   = round((results["passed"] / total_tests) * 100, 1) if total_tests else 0

summary = [
    [" Tests Passed",  results["passed"],   f"{pass_rate}%"],
    [" Tests Failed",  results["failed"],   ""],
    [" Warnings",     results["warnings"], ""],
    [" Total Tests",   total_tests,         ""],
]
print(tabulate(summary, headers=["Result", "Count", "Rate"], tablefmt="fancy_grid"))

# Overall verdict
print()
if results["failed"] == 0 and results["warnings"] == 0:
    print(f"{GREEN}{BOLD}   ALL TESTS PASSED! Your parser is working perfectly!{RESET}\n")
elif results["failed"] == 0:
    print(f"{YELLOW}{BOLD}   All tests passed but there are some warnings to review.{RESET}\n")
elif results["failed"] <= 3:
    print(f"{YELLOW}{BOLD}    Mostly passing — review the {results['failed']} failed test(s) above.{RESET}\n")
else:
    print(f"{RED}{BOLD}   Several tests failed — please review the errors above.{RESET}\n")

print(f"{BOLD}{'='*60}{RESET}\n")
