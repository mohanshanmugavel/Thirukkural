// Client controller for 3-Round Kural Game Engine

var currentRound = 1;
var round1SelectedWord = null;
var round1CorrectWord = "";
var round2UserWords = [];
var round2OriginalWords = [];
var confettiObj = null;

document.addEventListener("DOMContentLoaded", function () {
    // Initialize Confetti
    if (typeof ConfettiGenerator !== "undefined") {
        confettiObj = new ConfettiGenerator({ target: 'my-canvas' });
    }

    setupRound1();
    setupRound2();
});

function switchRound(roundNum) {
    if (roundNum === 2 && !kuralData.r1Completed) {
        alert("நிலை 2-ஐத் திறக்க நிலை 1-ஐ முடிக்க வேண்டும்!");
        return;
    }
    if (roundNum === 3 && !kuralData.r2Completed) {
        alert("நிலை 3-ஐத் திறக்க நிலை 2-ஐ முடிக்க வேண்டும்!");
        return;
    }

    currentRound = roundNum;

    document.querySelectorAll(".stepper-tab").forEach(tab => tab.classList.remove("active-tab"));
    document.querySelectorAll(".round-panel").forEach(panel => panel.style.display = "none");

    document.getElementById("tabRound" + roundNum).classList.add("active-tab");
    document.getElementById("panelRound" + roundNum).style.display = "block";
}

/* ==================== ROUND 1: CHOOSE WORD ==================== */
var distractorPool = [
    "நீடுவாழ்", "யாண்டும்", "தாள்சேர்ந்தார்க்", "இனிய", "பயன்என்று",
    "உளரென்று", "அன்போடு", "மணியினும்", "செல்வத்துள்", "சான்றோர்",
    "மிகுத்து", "பெருக்கல்", "கேடில்லை", "இல்லாள்தன்", "நாடொறும்",
    "மறந்தும்", "காதன்மை", "வாய்மை", "பொருட்டால்", "கேள்வி"
];

function setupRound1() {
    var words1 = kuralData.line1.split(" ");
    var words2 = kuralData.line2.split(" ");
    var allWords = words1.concat(words2);

    // Pick 1 word to mask (prefer middle words)
    var maskIdx = Math.floor(allWords.length / 2);
    round1CorrectWord = allWords[maskIdx];

    // Build masked text
    var maskedWords = allWords.slice();
    maskedWords[maskIdx] = "__________";

    var maskedLine1 = maskedWords.slice(0, words1.length).join(" ");
    var maskedLine2 = maskedWords.slice(words1.length).join(" ");

    var kuralTextEl = document.getElementById("round1KuralText");
    kuralTextEl.innerHTML = `<span>${maskedLine1}</span><br><span>${maskedLine2}</span>`;

    // Options
    var options = [round1CorrectWord];
    var shuffledPool = distractorPool.filter(w => w !== round1CorrectWord).sort(() => 0.5 - Math.random());
    options = options.concat(shuffledPool.slice(0, 3)).sort(() => 0.5 - Math.random());

    var gridEl = document.getElementById("round1OptionsGrid");
    gridEl.innerHTML = "";

    options.forEach(opt => {
        var chip = document.createElement("div");
        chip.className = "option-chip";
        chip.innerText = opt;
        chip.onclick = function () {
            document.querySelectorAll(".option-chip").forEach(c => c.classList.remove("selected-option"));
            chip.classList.add("selected-option");
            round1SelectedWord = opt;
            document.getElementById("submitRound1Btn").disabled = false;
        };
        gridEl.appendChild(chip);
    });
}

function checkRound1() {
    if (!round1SelectedWord) return;

    var btn = document.getElementById("submitRound1Btn");
    btn.disabled = true;
    btn.innerText = "சரிபார்க்கப்படுகிறது...";

    fetch("/api/round/evaluate_choose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            kuralId: kuralData.id,
            selected_word: round1SelectedWord,
            correct_word: round1CorrectWord
        })
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        btn.innerText = "சரிபார்க்க (Check)";
        var fb = document.getElementById("round1Feedback");

        if (data.is_correct) {
            fb.style.color = "#047857";
            fb.innerHTML = "✨ அருமை! சரியான விடை!";
            kuralData.r1Completed = true;

            document.getElementById("statusRound1").innerText = "✅";
            var tab2 = document.getElementById("tabRound2");
            tab2.classList.remove("disabled-tab");
            document.getElementById("statusRound2").innerText = "🔓";

            if (data.coins_rewarded > 0) {
                updateHeaderCoins(data.coins_rewarded, data.diamonds_rewarded);
                showRewardModal("நிலை 1 முடிந்தது! 🎉", "சரியான விடையைத் தேர்ந்தெடுத்துள்ளீர்கள்!", data.coins_rewarded, data.diamonds_rewarded);
                triggerConfetti();
            }

            setTimeout(() => switchRound(2), 1500);
        } else {
            fb.style.color = "#dc2626";
            fb.innerHTML = "❌ தவறான விடை. மீண்டும் முயற்சி செய்யவும்!";
        }
    })
    .catch(err => {
        btn.disabled = false;
        btn.innerText = "சரிபார்க்க (Check)";
    });
}

/* ==================== ROUND 2: ARRANGE WORDS ==================== */
function setupRound2() {
    var words1 = kuralData.line1.split(" ");
    var words2 = kuralData.line2.split(" ");
    round2OriginalWords = words1.concat(words2);

    resetRound2();
}

function resetRound2() {
    round2UserWords = [];
    var shuffled = round2OriginalWords.slice().sort(() => 0.5 - Math.random());

    var poolEl = document.getElementById("wordsPool");
    var slotsEl = document.getElementById("arrangeSlots");
    poolEl.innerHTML = "";
    slotsEl.innerHTML = "";
    document.getElementById("round2Feedback").innerHTML = "";

    shuffled.forEach((w, idx) => {
        var tile = document.createElement("div");
        tile.className = "word-tile";
        tile.innerText = w;
        tile.id = "poolTile_" + idx;
        tile.onclick = function () {
            moveToSlots(w, tile);
        };
        poolEl.appendChild(tile);
    });
}

function moveToSlots(word, tileEl) {
    round2UserWords.push(word);
    tileEl.style.display = "none";

    var slotsEl = document.getElementById("arrangeSlots");
    var slotTile = document.createElement("div");
    slotTile.className = "word-tile";
    slotTile.innerText = word;
    slotTile.onclick = function () {
        // Return back to pool
        var idx = round2UserWords.indexOf(word);
        if (idx > -1) round2UserWords.splice(idx, 1);
        slotsEl.removeChild(slotTile);
        tileEl.style.display = "inline-block";
    };
    slotsEl.appendChild(slotTile);
}

function checkRound2() {
    if (round2UserWords.length < round2OriginalWords.length) {
        alert("அனைத்து 7 சொற்களையும் வரிசைப்படுத்தவும்!");
        return;
    }

    var btn = document.getElementById("submitRound2Btn");
    btn.disabled = true;

    fetch("/api/round/evaluate_arrange", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            kuralId: kuralData.id,
            words: round2UserWords
        })
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        var fb = document.getElementById("round2Feedback");

        if (data.is_correct) {
            fb.style.color = "#047857";
            fb.innerHTML = "✨ மிகச் சிறப்பு! அனைத்து சொற்களும் சரியான வரிசையில் உள்ளன!";
            kuralData.r2Completed = true;

            document.getElementById("statusRound2").innerText = "✅";
            var tab3 = document.getElementById("tabRound3");
            tab3.classList.remove("disabled-tab");
            document.getElementById("statusRound3").innerText = "🔓";

            if (data.coins_rewarded > 0) {
                updateHeaderCoins(data.coins_rewarded, data.diamonds_rewarded);
                showRewardModal("நிலை 2 முடிந்தது! 🧩", "சொற்களைச் சரியாக வரிசைப்படுத்தியுள்ளீர்கள்!", data.coins_rewarded, data.diamonds_rewarded);
                triggerConfetti();
            }

            setTimeout(() => switchRound(3), 1500);
        } else {
            fb.style.color = "#dc2626";
            fb.innerHTML = "❌ சில சொற்கள் தவறான நிலையில் உள்ளன. சிவப்பு நிறத்தில் உள்ளவற்றை சரிபார்க்கவும்!";

            // Highlight error slots
            var slotTiles = document.querySelectorAll("#arrangeSlots .word-tile");
            if (data.mismatched_indices) {
                data.mismatched_indices.forEach(i => {
                    if (slotTiles[i]) slotTiles[i].classList.add("error-tile");
                });
            }
        }
    });
}

/* ==================== ROUND 3 & UTILITIES ==================== */
function handleVoiceResult(accuracy, stars, resultData) {
    fetch("/api/round/evaluate_voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            kuralId: kuralData.id,
            accuracy: accuracy
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.is_passed) {
            kuralData.r3Completed = true;
            document.getElementById("statusRound3").innerText = "✅";

            if (data.coins_rewarded > 0 || data.bonus_coins > 0) {
                var totalC = data.coins_rewarded + data.bonus_coins;
                var totalD = data.diamonds_rewarded + data.bonus_diamonds;
                updateHeaderCoins(totalC, totalD);

                var msg = "உங்கள் குரல் உச்சரிப்பு சிறப்பாக உள்ளது!";
                if (data.badge_awarded) {
                    msg += " நீங்கள் 'Kural Master' பேட்ஜ் வென்றுள்ளீர்கள்!";
                }
                showRewardModal("குறள் நிறைவடைந்தது! 🏆", msg, totalC, totalD, data.badge_awarded);
                triggerConfetti();
            }
        }
    });
}

function updateHeaderCoins(addedCoins, addedDiamonds) {
    var cEl = document.getElementById("header-coins");
    var dEl = document.getElementById("header-diamonds");
    if (cEl) cEl.innerText = parseInt(cEl.innerText || "0") + addedCoins;
    if (dEl) dEl.innerText = parseInt(dEl.innerText || "0") + addedDiamonds;
}

function showRewardModal(title, msg, coins, diamonds, badgeName) {
    document.getElementById("modalTitle").innerText = title;
    document.getElementById("modalMessage").innerText = msg;
    document.getElementById("modalCoins").innerText = coins;
    document.getElementById("modalDiamonds").innerText = diamonds;

    if (badgeName) {
        document.getElementById("modalBadgeName").innerText = badgeName;
        document.getElementById("modalBadgeContainer").style.display = "block";
    } else {
        document.getElementById("modalBadgeContainer").style.display = "none";
    }

    document.getElementById("rewardModal").style.display = "flex";
}

function closeRewardModal() {
    document.getElementById("rewardModal").style.display = "none";
    if (confettiObj) confettiObj.clear();
}

function triggerConfetti() {
    if (confettiObj) {
        confettiObj.render();
        setTimeout(() => confettiObj.clear(), 3500);
    }
}

function playKuralAudio() {
    var kuralId = kuralData.id;
    var x = document.getElementById("myAudio");
    fetch('/get_kural_audio/' + kuralId)
        .then(res => res.json())
        .then(data => {
            if (data.audio_url) {
                x.src = data.audio_url;
                x.load();
                x.play();
            }
        });
}
