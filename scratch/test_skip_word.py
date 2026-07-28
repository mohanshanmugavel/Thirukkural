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

def evaluate_speech_current(kural_words_original, spoken_words):
    word_statuses = []
    wrong_words = []
    missing_words = []
    correct_count = 0
    used_spoken = set()
    current_spoken_cursor = 0

    for idx, exp_word in enumerate(kural_words_original):
        best_score = 0.0
        best_said = ""
        best_indices = []

        search_start = max(0, current_spoken_cursor - 1)

        for j in range(search_start, len(spoken_words)):
            if j in used_spoken:
                continue
            sp_word = spoken_words[j]
            score = compute_tamil_word_similarity(exp_word, sp_word)
            if score > best_score:
                best_score = score
                best_said = sp_word
                best_indices = [j]

        for j in range(search_start, len(spoken_words) - 1):
            if j in used_spoken and (j+1) in used_spoken:
                continue
            combo = spoken_words[j] + spoken_words[j+1]
            score = compute_tamil_word_similarity(exp_word, combo)
            if score > best_score:
                best_score = score
                best_said = spoken_words[j] + " " + spoken_words[j+1]
                best_indices = [j, j+1]

        if best_score >= 0.60:
            word_statuses.append({"word": exp_word, "status": "correct", "score": best_score})
            correct_count += 1
            used_spoken.update(best_indices)
            if best_indices:
                current_spoken_cursor = max(best_indices) + 1
        elif best_score > 0.30:
            word_statuses.append({"word": exp_word, "status": "wrong", "score": best_score})
            wrong_words.append({"expected": exp_word, "said": best_said})
            used_spoken.update(best_indices)
            if best_indices:
                current_spoken_cursor = max(best_indices) + 1
        else:
            word_statuses.append({"word": exp_word, "status": "missing", "score": 0.0})
            missing_words.append(exp_word)

    total_words = len(kural_words_original)
    accuracy = int((correct_count / total_words) * 100) if total_words > 0 else 0

    return accuracy, correct_count, total_words, word_statuses

kural37 = ["அறத்தாறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]

# User skips Word 1 ("அறத்தாறு") and speaks words 2-7 ("இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"):
spoken_skip_word1 = ["இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]

acc, c, t, statuses = evaluate_speech_current(kural37, spoken_skip_word1)
print(f"Skipping Word 1 -> Accuracy: {acc}%, Count: {c}/{t}")
for idx, s in enumerate(statuses):
    print(f"  Word {idx+1} ({kural37[idx]}): {s['status']} (score: {s['score']:.2f})")
