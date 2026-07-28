# -*- coding: utf-8 -*-
import string
import difflib

def normalize_tamil_phonetic(text):
    if not text:
        return ""
    text = text.strip(string.punctuation)
    
    # 1. Grantha letters to native Tamil
    grantha = [
        ('ஷ', 'ச'), ('ஸ', 'ச'), ('ஜ', 'ச'), ('ஹ', 'க'), ('ஃ', '')
    ]
    for k, v in grantha:
        text = text.replace(k, v)

    # 2. Colloquial slang suffix removal for words > 4 chars
    slang_suffixes = ['ங்களின்', 'ங்கள்', 'ங்க', 'னு', 'டா', 'ப்பா', 'மா', 'லா', 'வே', 'மு']
    for sfx in slang_suffixes:
        if len(text) > 4 and text.endswith(sfx):
            text = text[:-len(sfx)]
            break

    # 3. Phonetic child speech & dialect transformations
    replacements = [
        ('ஆ', 'அ'), ('ஈ', 'இ'), ('ஊ', 'உ'), ('ஏ', 'எ'), ('ஓ', 'ஒ'), ('ஐ', 'அஇ'), ('ஔ', 'அஉ'),
        ('ா', ''), ('ீ', 'ி'), ('ூ', 'ு'), ('ே', 'ெ'), ('ோ', 'ொ'), ('ை', 'ெ'),
        ('ற', 'ர'), ('ன', 'ந'), ('ண', 'ந'), ('ள', 'ல'), ('ழ', 'ல'),
        ('க்', 'க'), ('ச்', 'ச'), ('ட்', 'ட'), ('த்', 'த'), ('ப்', 'ப'), ('ற்', 'ர'),
        ('ன்', 'ந'), ('ங்', 'ங'), ('ஞ்', 'ஞ'), ('ண்', 'ந'), ('ந்', 'ந'),
        ('ம்ப', 'ம'), ('ம்', 'ம'), ('ய்', 'ய'), ('ர்', 'ர'), ('ல்', 'ல'), ('வ்', 'வ'), ('ழ்', 'ல'), ('ள்', 'ல')
    ]
    res = text
    for k, v in replacements:
        res = res.replace(k, v)
    return res

def compute_tamil_word_similarity(w1, w2):
    if not w1 or not w2:
        return 0.0
    w1_c = w1.strip(string.punctuation)
    w2_c = w2.strip(string.punctuation)
    if not w1_c or not w2_c:
        return 0.0
    if w1_c == w2_c:
        return 1.0
    
    raw_ratio = difflib.SequenceMatcher(None, w1_c, w2_c).ratio()
    n1 = normalize_tamil_phonetic(w1_c)
    n2 = normalize_tamil_phonetic(w2_c)
    norm_ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
    
    # Substring / syllabic overlap ratio for partial spoken words
    sub_ratio = 0.0
    if len(n1) > 2 and len(n2) > 2:
        if n1 in n2 or n2 in n1:
            sub_ratio = min(len(n1), len(n2)) / max(len(n1), len(n2))

    return max(raw_ratio, norm_ratio, sub_ratio)

def run_tests():
    test_cases = [
        ("அறத்தாறு", "ஆரத் ஆறு", True),
        ("அறத்தாறு", "ஆரத்தாறு", True),
        ("பொறுத்தானோடு", "பொருத்தானொடு", True),
        ("பொறுத்தானோடு", "பொருத்தமானது", True),
        ("சிவிகை", "சிலுவை", True),
        ("அகர", "ஆஹர", True),
        ("முதல", "முதலா", True),
        ("எழுத்தெல்லாம்", "எலுத்தெல்லாம்", True),
        ("வணக்கம்", "பள்ளி", False)
    ]

    print("--- Running Phonetic Child Slang Tests ---")
    for exp, spoken, expected_match in test_cases:
        score = compute_tamil_word_similarity(exp, spoken)
        matched = score >= 0.50
        status = "PASS" if matched == expected_match else "FAIL"
        print(f"[{status}] Expected: '{exp}', Spoken: '{spoken}', Score: {score:.2f}, Matched: {matched}")

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    run_tests()
