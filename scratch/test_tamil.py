# -*- coding: utf-8 -*-
import difflib

def normalize_tamil(text):
    # Homophone & Vowel length normalization for Speech-To-Text comparison
    replacements = {
        'ஆ': 'அ', 'ஈ': 'இ', 'ஊ': 'உ', 'ஏ': 'எ', 'ஓ': 'ஒ',
        'ா': '', 'ீ': 'ி', 'ூ': 'ு', 'ே': 'ெ', 'ோ': 'ொ', 'ை': 'ெ',
        'ற': 'ர',
        'ன': 'ந', 'ண': 'ந',
        'ள': 'ல', 'ழ': 'ல',
        'க்': 'க', 'ச்': 'ச', 'ட்': 'ட', 'த்': 'த', 'ப்': 'ப', 'ற்': 'ர', 'ன்': 'ந', 'ங்': 'ங', 'ஞ்': 'ஞ', 'ண்': 'ந', 'ந்': 'ந', 'ம்ப': 'ம', 'ம்': 'ம', 'ய்': 'ய', 'ர்': 'ர', 'ல்': 'ல', 'வ்': 'வ', 'ழ்': 'ல', 'ள்': 'ல'
    }
    res = text
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res

def get_tamil_similarity(w1, w2):
    # 1. Direct raw ratio
    raw_ratio = difflib.SequenceMatcher(None, w1, w2).ratio()
    
    # 2. Normalized phonetic ratio
    n1 = normalize_tamil(w1)
    n2 = normalize_tamil(w2)
    norm_ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
    
    return max(raw_ratio, norm_ratio)

test_pairs = [
    ('அறத்தாறு', 'ஆரத் ஆறு'),
    ('அறத்தாறு', 'ஆரத்ஆறு'),
    ('அறத்தாறு', 'அரத்தாறு'),
    ('பொறுத்தானோடு', 'பொருத்தமானது'),
    ('சிவிகை', 'சிலுவை'),
]

for w1, w2 in test_pairs:
    w2_clean = w2.replace(" ", "")
    sim = get_tamil_similarity(w1, w2_clean)
    raw_sim = difflib.SequenceMatcher(None, w1, w2_clean).ratio()
    norm_sim = difflib.SequenceMatcher(None, normalize_tamil(w1), normalize_tamil(w2_clean)).ratio()
    print(f"pair: {raw_sim:.3f} | norm: {norm_sim:.3f} | max: {sim:.3f}")
