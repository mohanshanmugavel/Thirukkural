# -*- coding: utf-8 -*-
import difflib
import string

def normalize_tamil_phonetic(text):
    if not text:
        return ""
    # Map long vowels & homophones for Tamil STT comparison
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

def compute_word_similarity(w1, w2):
    if not w1 or not w2:
        return 0.0
    w1_clean = w1.strip(string.punctuation)
    w2_clean = w2.strip(string.punctuation)
    
    if w1_clean == w2_clean:
        return 1.0
        
    raw_ratio = difflib.SequenceMatcher(None, w1_clean, w2_clean).ratio()
    
    n1 = normalize_tamil_phonetic(w1_clean)
    n2 = normalize_tamil_phonetic(w2_clean)
    norm_ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
    
    return max(raw_ratio, norm_ratio)

kural_words = ["அறத்தாறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]
spoken_words = ["ஆரத்", "ஆறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]

print("Evaluating word matching:")
for idx, exp_word in enumerate(kural_words):
    # Test matching against single spoken words and adjacent spoken word pairs
    best_match_score = 0.0
    best_spoken = ""
    
    for s_idx in range(len(spoken_words)):
        # Single word check
        score1 = compute_word_similarity(exp_word, spoken_words[s_idx])
        if score1 > best_match_score:
            best_match_score = score1
            best_spoken = spoken_words[s_idx]
            
        # Pair check (e.g. "ஆரத்" + "ஆறு" -> "ஆரத்ஆறு")
        if s_idx + 1 < len(spoken_words):
            combined_spoken = spoken_words[s_idx] + spoken_words[s_idx + 1]
            score2 = compute_word_similarity(exp_word, combined_spoken)
            if score2 > best_match_score:
                best_match_score = score2
                best_spoken = spoken_words[s_idx] + " " + spoken_words[s_idx + 1]
                
    is_correct = (best_match_score >= 0.65)
    print(f"Word {idx+1}: score {best_match_score:.3f} | Correct: {is_correct}")
