# -*- coding: utf-8 -*-
import string
import difflib
import re
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def split_tamil_syllables(text):
    """Split Tamil text into grapheme clusters / syllables."""
    if not text:
        return []
    text = text.strip(string.punctuation)
    # Match a base character followed by dependent vowel signs / pulli
    pattern = r'[\u0B85-\u0B94\u0B95-\u0BB9][\u0BBE-\u0BCD\u0BD7]*'
    return re.findall(pattern, text)

def normalize_syllable(s):
    """Normalize child sound variations at syllable level."""
    # Grantha
    s = s.replace('ஷ', 'ச').replace('ஸ', 'ச').replace('ஜ', 'ச').replace('ஹ', 'க').replace('ஃ', '')
    # Sound swaps
    s = s.replace('ற', 'ர').replace('ன', 'ந').replace('ண', 'ந').replace('ள', 'ல').replace('ழ', 'ல')
    # Vowels
    s = s.replace('ஆ', 'அ').replace('ஈ', 'இ').replace('ஊ', 'உ').replace('ஏ', 'எ').replace('ஓ', 'ஒ')
    s = s.replace('ா', '').replace('ீ', 'ி').replace('ூ', 'ு').replace('ே', 'ெ').replace('ோ', 'ொ').replace('ை', 'ெ')
    return s

def compute_tamil_word_similarity(w1, w2):
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

    # Raw syllable sequence ratio
    raw_syl_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()

    # Phonetic normalized syllable ratio
    ns1 = [normalize_syllable(x) for x in s1]
    ns2 = [normalize_syllable(x) for x in s2]
    norm_syl_ratio = difflib.SequenceMatcher(None, ns1, ns2).ratio()

    return max(raw_syl_ratio, norm_syl_ratio)

def run_tests():
    test_cases = [
        ("அறத்தாறு", "ஆரத்தாறு", "correct"),
        ("அறத்தாறு", "ஆரத் ஆறு", "correct"),
        ("எழுத்தெல்லாம்", "எலுத்தெல்லாம்", "correct"),
        ("பொறுத்தானோடு", "பொருத்தானொடு", "correct"),
        ("சிவிகை", "சிவிக", "correct"),
        ("சிவிகை", "சிலுவை", "wrong"),
        ("பொறுத்தானோடு", "பொருத்தமானது", "wrong"),
        ("அறத்தாறு", "வணக்கம்", "missing"),
    ]

    print("--- Running Syllable-Based Tamil Similarity Tests ---")
    all_passed = True
    for exp, spoken, expected_status in test_cases:
        score = compute_tamil_word_similarity(exp, spoken)
        if score >= 0.65:
            status = "correct"
        elif score >= 0.30:
            status = "wrong"
        else:
            status = "missing"
        
        passed = (status == expected_status)
        if not passed:
            all_passed = False
        tag = "PASS" if passed else "FAIL"
        print(f"[{tag}] Expected: '{exp}', Spoken: '{spoken}' => Score: {score:.2f} | Status: {status} (Expected: {expected_status})")

    print("\nOVERALL TEST RESULT:", "ALL PASSED" if all_passed else "SOME FAILED")

if __name__ == "__main__":
    run_tests()
