# -*- coding: utf-8 -*-
import string
import difflib
import re
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def split_tamil_syllables(text):
    if not text:
        return []
    text = text.strip(string.punctuation)
    pattern = r'[\u0B85-\u0B94\u0B95-\u0BB9][\u0BBE-\u0BCD\u0BD7]*'
    return re.findall(pattern, text)

def normalize_syllable_child(s):
    # Grantha letters
    s = s.replace('ஷ', 'ச').replace('ஸ', 'ச').replace('ஜ', 'ச').replace('ஹ', 'க').replace('ஃ', '')
    # Child sound swaps ('ழ'->'ல', 'ற'->'ர', 'ண'/'ன'->'ந', 'ள'->'ல')
    s = s.replace('ற', 'ர').replace('ன', 'ந').replace('ண', 'ந').replace('ள', 'ல').replace('ழ', 'ல')
    # Vowel duration invariance
    s = s.replace('ஆ', 'அ').replace('ஈ', 'இ').replace('ஊ', 'உ').replace('ஏ', 'எ').replace('ஓ', 'ஒ')
    s = s.replace('ா', '').replace('ீ', 'ி').replace('ூ', 'ு').replace('ே', 'ெ').replace('ோ', 'ொ').replace('ை', 'ெ')
    return s

def normalize_syllable_adult(s):
    # Adult mode: strict - no sound swaps ('ழ' stays 'ழ', 'ற' stays 'ற')
    # Only clean punctuation/spaces
    return s

def compute_tamil_word_similarity(w1, w2, mode="child"):
    if not w1 or not w2:
        return 0.0
    w1_c = w1.strip(string.punctuation)
    w2_c = w2.strip(string.punctuation)
    if not w1_c or not w2_c:
        return 0.0
    if w1_c == w2_c:
        return 1.0

    s1 = split_tamil_syllables(w1_c)
    s2 = split_tamil_syllables(w2_c)
    
    if not s1 or not s2:
        return difflib.SequenceMatcher(None, w1_c, w2_c).ratio()

    raw_syl_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()

    if mode == "child":
        ns1 = [normalize_syllable_child(x) for x in s1]
        ns2 = [normalize_syllable_child(x) for x in s2]
        norm_syl_ratio = difflib.SequenceMatcher(None, ns1, ns2).ratio()
        return max(raw_syl_ratio, norm_syl_ratio)
    else:
        # Adult mode: strict syllable matching
        ns1 = [normalize_syllable_adult(x) for x in s1]
        ns2 = [normalize_syllable_adult(x) for x in s2]
        norm_syl_ratio = difflib.SequenceMatcher(None, ns1, ns2).ratio()
        return max(raw_syl_ratio, norm_syl_ratio)

def evaluate_word(exp, spoken, mode):
    score = compute_tamil_word_similarity(exp, spoken, mode=mode)
    cutoff = 0.60 if mode == "child" else 0.85
    status = "correct" if score >= cutoff else "wrong"
    return score, status

def run_tests():
    test_cases = [
        ("எழுத்தெல்லாம்", "எலுத்தெல்லாம்"), # 'ழ' pronounced as 'ல'
        ("அறத்தாறு", "ஆரத்தாறு"),         # 'ற' pronounced as 'ர'
        ("அறத்தாறு", "அறத்தாறு"),         # Exact perfect pronunciation
        ("பொறுத்தானோடு", "பொருத்தானொடு"),   # Child short vowel / 'ற'->'ர'
    ]

    print("=== Testing Child Mode vs Adult Mode ===")
    for exp, spoken in test_cases:
        score_child, status_child = evaluate_word(exp, spoken, mode="child")
        score_adult, status_adult = evaluate_word(exp, spoken, mode="adult")
        print(f"Exp: '{exp}' | Spoken: '{spoken}'")
        print(f"  👶 Child Mode : Score = {score_child:.2f} => Status = {status_child}")
        print(f"  👨 Adult Mode : Score = {score_adult:.2f} => Status = {status_adult}")
        print("-" * 50)

if __name__ == "__main__":
    run_tests()
