# -*- coding: utf-8 -*-
import difflib
import string

def normalize_tamil_phonetic(text):
    if not text:
        return ""
    text = text.strip(string.punctuation)
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
    return max(raw_ratio, norm_ratio)

def evaluate_speech(kural_words_original, spoken_words):
    word_statuses = []
    wrong_words = []
    missing_words = []
    correct_count = 0
    used_spoken = set()

    for idx, exp_word in enumerate(kural_words_original):
        best_score = 0.0
        best_said = ""
        best_spoken_indices = []

        # 1. Search single spoken words
        for j, sp_word in enumerate(spoken_words):
            score = compute_tamil_word_similarity(exp_word, sp_word)
            if score > best_score:
                best_score = score
                best_said = sp_word
                best_spoken_indices = [j]

        # 2. Search 2-word combinations (e.g. "ஆரத்" + "ஆறு")
        for j in range(len(spoken_words) - 1):
            combo = spoken_words[j] + spoken_words[j+1]
            score = compute_tamil_word_similarity(exp_word, combo)
            if score > best_score:
                best_score = score
                best_said = spoken_words[j] + " " + spoken_words[j+1]
                best_spoken_indices = [j, j+1]

        # Categorize based on score threshold
        if best_score >= 0.60:
            word_statuses.append({"word": exp_word, "status": "correct", "score": best_score})
            correct_count += 1
            used_spoken.update(best_spoken_indices)
        elif best_score > 0.30:
            word_statuses.append({"word": exp_word, "status": "wrong", "score": best_score})
            wrong_words.append({"expected": exp_word, "said": best_said})
            used_spoken.update(best_spoken_indices)
        else:
            word_statuses.append({"word": exp_word, "status": "missing", "score": best_score})
            missing_words.append(exp_word)

    extra_words = [sp for j, sp in enumerate(spoken_words) if j not in used_spoken]
    total_words = len(kural_words_original)
    accuracy = int((correct_count / total_words) * 100) if total_words > 0 else 0

    return accuracy, correct_count, total_words, word_statuses, wrong_words, missing_words, extra_words

# Test Kural 37 with actual user spoken output from screenshot:
kural37 = ["அறத்தாறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]
spoken_user = ["ஆரத்", "ஆறு", "இதுவென", "வேண்டா", "சிலுவை", "பொருத்தமானது", "ஊர்ந்தான்", "இடை"]

acc, count, total, statuses, wrong, missing, extra = evaluate_speech(kural37, spoken_user)
print(f"User Spoken Accuracy: {acc}%, Count: {count}/{total}")

wrong_spoken = ["வணக்கம்", "பள்ளி", "ஆசிரியர்"]
acc2, count2, total2, statuses2, wrong2, missing2, extra2 = evaluate_speech(kural37, wrong_spoken)
print(f"Wrong Spoken Accuracy: {acc2}%, Count: {count2}/{total2}")
