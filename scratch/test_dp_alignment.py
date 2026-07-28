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

def evaluate_speech_dp(kural_words_original, spoken_words):
    N = len(kural_words_original)
    M = len(spoken_words)
    
    # 1. Build all candidate match edges
    # A candidate edge is (i, j_start, j_end, score, spoken_text)
    candidates = []
    for i in range(N):
        exp_w = kural_words_original[i]
        # Single spoken word check
        for j in range(M):
            score = compute_tamil_word_similarity(exp_w, spoken_words[j])
            if score >= 0.50:
                candidates.append((i, j, j + 1, score, spoken_words[j]))
        # 2-word combination check
        for j in range(M - 1):
            combo = spoken_words[j] + spoken_words[j+1]
            score = compute_tamil_word_similarity(exp_w, combo)
            if score >= 0.50:
                candidates.append((i, j, j + 2, score, spoken_words[j] + " " + spoken_words[j+1]))

    # Sort candidates by score descending
    candidates.sort(key=lambda x: x[3], reverse=True)

    # 2. Dynamic Programming / Max Weight Independent Set in DAG to find optimal monotonic alignment
    # We want a subset of candidates such that for chosen candidates c1, c2:
    # c1.i < c2.i AND c1.j_end <= c2.j_start
    # Let's find max score subset using DP over (i, j)
    dp = {} # (i_idx, j_idx) -> (max_score, list_of_chosen_candidates)

    # Convert candidates to list sorted by i then j_start
    cand_sorted = sorted(candidates, key=lambda c: (c[0], c[1]))

    # DP state: dp[c_idx] = max score ending at candidate c_idx
    best_overall_score = 0.0
    best_path = []

    memo = {}
    def solve(cand_idx):
        if cand_idx in memo:
            return memo[cand_idx]
        
        curr = cand_sorted[cand_idx]
        max_s = curr[3]
        max_p = [curr]

        for next_idx in range(cand_idx + 1, len(cand_sorted)):
            nxt = cand_sorted[next_idx]
            # Enforce strict monotonic progression in both Kural word index and Spoken word index
            if nxt[0] > curr[0] and nxt[1] >= curr[2]:
                sub_s, sub_p = solve(next_idx)
                if curr[3] + sub_s > max_s:
                    max_s = curr[3] + sub_s
                    max_p = [curr] + sub_p

        memo[cand_idx] = (max_s, max_p)
        return memo[cand_idx]

    for idx in range(len(cand_sorted)):
        score, path = solve(idx)
        if score > best_overall_score:
            best_overall_score = score
            best_path = path

    # Map matched candidates back to expected words
    matched_map = {c[0]: c for c in best_path}
    used_spoken = set()
    for c in best_path:
        for sj in range(c[1], c[2]):
            used_spoken.add(sj)

    word_statuses = []
    wrong_words = []
    missing_words = []
    correct_count = 0

    for i in range(N):
        exp_w = kural_words_original[i]
        if i in matched_map:
            c = matched_map[i]
            score = c[3]
            said_text = c[4]
            if score >= 0.60:
                word_statuses.append({"word": exp_w, "status": "correct", "score": score})
                correct_count += 1
            else:
                word_statuses.append({"word": exp_w, "status": "wrong", "score": score})
                wrong_words.append({"expected": exp_w, "said": said_text})
        else:
            word_statuses.append({"word": exp_w, "status": "missing", "score": 0.0})
            missing_words.append(exp_w)

    extra_words = [sp for j, sp in enumerate(spoken_words) if j not in used_spoken]
    accuracy = int((correct_count / N) * 100) if N > 0 else 0

    return accuracy, correct_count, N, word_statuses, wrong_words, missing_words, extra_words

# Test cases:
kural37 = ["அறத்தாறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]

# 1. Full Correct Order:
s1 = ["ஆரத்", "ஆறு", "இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]
acc1, c1, t1, st1, w1, m1, e1 = evaluate_speech_dp(kural37, s1)
print(f"1. Full Correct Order -> Acc: {acc1}%, Count: {c1}/{t1}, Missing: {m1}")

# 2. Skip Word 1 (User speaks words 2-7):
s2 = ["இதுவென", "வேண்டா", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]
acc2, c2, t2, st2, w2, m2, e2 = evaluate_speech_dp(kural37, s2)
print(f"2. Skip Word 1 -> Acc: {acc2}%, Count: {c2}/{t2}, Missing count: {len(m2)}")

# 3. Random / Shuffled Word Order (Words in wrong order):
s3 = ["இடை", "ஊர்ந்தான்", "சிவிகை", "வேண்டா", "இதுவென", "ஆரத்", "ஆறு", "பொறுத்தானோடு"]
s4 = ["ஆரத்", "ஆறு", "இதுவென", "சிவிகை", "பொறுத்தானோடு", "ஊர்ந்தான்", "இடை"]
acc4, c4, t4, st4, w4, m4, e4 = evaluate_speech_dp(kural37, s4)
print(f"4. Skip Word 3 -> Acc: {acc4}%, Count: {c4}/{t4}, Missing count: {len(m4)}")
