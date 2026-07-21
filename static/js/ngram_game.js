// N-gram Prediction Game JavaScript

// Game state variables
var currentKural = null;
var userTimerStart = null;
var userTimerInterval = null;
var userTimeMs = 0;
var gameState = 'waiting'; // 'waiting', 'playing', 'submitted', 'results'
var selectedOptions = {}; // selections keyed by masked index string

// Helper: Fisher-Yates shuffle
function shuffleArray(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

// Initialize game on page load
$(document).ready(function() {
    loadNewKural();
    loadLeaderboard();
});

/**
 * Load a new random kural with masked word
 */
function loadNewKural() {
    // Reset game state
    gameState = 'waiting';
    userTimeMs = 0;
    currentKural = null;
    $('#submit-answer-btn').show();
    $('#next-kural-btn').hide();
    $('#results-container').hide();
    $('#kural-vilakam-container').hide();
    $('#timer-display').text('0.0');
    selectedOptions = {};
    
    // Clear any existing timer
    if (userTimerInterval) {
        clearInterval(userTimerInterval);
        userTimerInterval = null;
    }
    
    // Fetch new kural
    $.ajax({
        url: '/ngram/get_kural',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            currentKural = response;
            // show adhigaram and full lines
            $('#aadhigaram-name').text(response.aadhigaram || '-');
            // hide full kural lines and show only masked kural in Thirukkural format (4-3)
            $('#kural-line1').text('');
            $('#kural-line2').text('');
            var masked = response.masked_line || '';
            // split into words and format into 4 + rest (commonly 4-3 for kural)
            var words = masked.split(' ').filter(function(w){ return w.trim().length>0; });
            var first = words.slice(0,4).join(' ');
            var second = words.slice(4).join(' ');
            var display = '';
            if (second) display = '<p class="kural">' + first + '</p><p class="kural">' + second + '</p>';
            else display = '<p class="kural">' + first + '</p>';
            $('#masked-line-text').html(display);

            // render options for each masked index into options-0, options-1 using fillups-style pool
            $('.option-tiles').empty();
            selectedOptions = {};
            var options_pool = ["நீடுவாழ்", "யாண்டும்", "தாள்சேர்ந்தார்க்", "இனிய", "பயன்என்று",
                "உளரென்று", "அன்போடு", "மணியினும்", "செல்வத்துள்", "சான்றோர்",
                "மிகுத்து", "பெருக்கல்", "கேடில்லை", "இல்லாள்தன்", "நாடொறும்",
                "மறந்தும்", "காதன்மை", "வாய்மை", "பொருட்டால்", "கேள்வி",
                "மாண்ட", "படிபொறை", "தம்மைப்", "உளராக", "இடும்பை",
                "சால்பின்", "துறந்தார்", "கொடியன", "நாணுடைமை", "விரும்பி",
                "குழவி", "அம்மா", "நுகர்வார்", "அறத்தான்", "மாண்பு",
                "தொடர்ந்து", "விளக்கம்", "முன்னேறல்", "நிலைமை", "ஒழுக்கம்",
                "பிறப்பொடு", "துன்பம்", "தோன்றும்", "உணர்ச்சி", "உயர்ச்சி",
                "அடக்கம்", "செல்வம்", "பெருமை", "நன்றி"];
            var masked = response.masked_indices || [];
            masked.forEach(function(idx, pos) {
                var key = String(idx);
                var container = '#options-' + pos;
                $(container).empty();
                // create choices: 3 random from pool + correct word
                var pool = options_pool.filter(function(w){ return w !== response.correct_words[key]; });
                shuffleArray(pool);
                var choices = pool.slice(0,3);
                choices.push(response.correct_words[key]);
                shuffleArray(choices);
                choices.forEach(function(choice) {
                    var tile = $('<button>').addClass('option-tile').text(choice).css({padding:'8px 12px', borderRadius:'8px', border:'1px solid #333', background:'#fff'});
                    tile.on('click', function(){ selectOption(key, choice, container, tile); });
                    $(container).append(tile);
                });
            });

            startUserTimer();
            gameState = 'playing';
        },
        error: function(xhr, status, error) {
            console.error('Error loading kural:', error);
            $('#masked-line-text').text('குறள் ஏற்றுவதில் பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.');
        }
    });
}

/**
 * Display the masked kural line
 */
function displayMaskedLine(maskedLine) {
    // Format the line for better display (handle multiple words per line)
    var words = maskedLine.split(' ');
    var formattedLine = words.join(' ');
    $('#masked-line-text').text(formattedLine);
}

/**
 * Start the user timer
 */
function startUserTimer() {
    userTimerStart = Date.now();
    userTimerInterval = setInterval(function() {
        var elapsed = (Date.now() - userTimerStart) / 1000;
        $('#timer-display').text(elapsed.toFixed(1));
        userTimeMs = Date.now() - userTimerStart;
    }, 100); // Update every 100ms for smooth display
}

/**
 * Stop the user timer
 */
function stopUserTimer() {
    if (userTimerInterval) {
        clearInterval(userTimerInterval);
        userTimerInterval = null;
    }
    if (userTimerStart) {
        userTimeMs = Date.now() - userTimerStart;
    }
}

/**
 * Submit user answer and get machine prediction
 */
function submitUserAnswer() {
    if (gameState !== 'playing' || !currentKural) {
        return;
    }
    // Build user answers array in the same order as masked_indices
    var maskedIdxs = currentKural.masked_indices || [];
    var userAnswers = [];
    for (var i=0;i<maskedIdxs.length;i++){
        var key = String(maskedIdxs[i]);
        var ans = selectedOptions[key] || '';
        userAnswers.push(ans);
    }
    // Validate selections
    var allSelected = userAnswers.every(function(a){ return a && a.length>0; });
    if (!allSelected) {
        alert('தயவுசெய்து ஒவ்வொரு இடத்திற்கும் விடையை தேர்வு செய்க.');
        return;
    }

    // Stop user timer
    stopUserTimer();
    gameState = 'submitted';
    $('#submit-answer-btn').hide();

    // Get machine prediction
    getMachinePrediction(userAnswers);
}

/**
 * Get machine prediction using N-gram model
 */
function getMachinePrediction(userAnswer) {
    var machineStartTime = Date.now();
    
    $.ajax({
        url: '/ngram/predict',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            masked_line: currentKural.masked_line,
            masked_indices: currentKural.masked_indices
        }),
        dataType: 'json',
        success: function(response) {
            var machineTimeMs = response.machine_time_ms || (Date.now() - machineStartTime);
            var predictions = response.predictions || [];
            displayResults(userAnswer, predictions, machineTimeMs);
        },
        error: function(xhr, status, error) {
            console.error('Error getting prediction:', error);
            // Still display results with empty prediction
            displayResults(userAnswer, [], 0);
        }
    });
}

/**
 * Display comparison results
 */
function displayResults(userAnswer, machinePrediction, machineTimeMs) {
    var maskedIdxs = currentKural.masked_indices || [];
    var correctWords = currentKural.correct_words || {};

    var userAnswers = Array.isArray(userAnswer) ? userAnswer : [userAnswer];
    var machineAnswers = Array.isArray(machinePrediction) ? machinePrediction : [machinePrediction];

    var userHtml = '';
    var machineHtml = '';
    var userCorrectAll = true;
    var machineCorrectAll = true;
    for (var i=0;i<maskedIdxs.length;i++){
        var idx = maskedIdxs[i];
        var key = String(idx);
        var correct = correctWords[key] || '';
        var uAns = userAnswers[i] || '';
        var mAns = machineAnswers[i] || '';
        var uCorrect = (uAns === correct);
        var mCorrect = (mAns === correct);
        if (!uCorrect) userCorrectAll = false;
        if (!mCorrect) machineCorrectAll = false;
        userHtml += '<div>' + (uCorrect ? '✓' : '✗') + ' ' + (uAns || '(none)') + '</div>';
        machineHtml += '<div>' + (mCorrect ? '✓' : '✗') + ' ' + (mAns || '(none)') + '</div>';
    }

    $('#user-result').html(userHtml);
    $('#user-time').text('நேரம்: ' + (userTimeMs / 1000).toFixed(2) + ' வினாடிகள்');

    $('#machine-result').html(machineHtml);
    $('#machine-time').text('நேரம்: ' + (machineTimeMs / 1000).toFixed(2) + ' வினாடிகள்');

    // Display correct words
    var correctHtml = 'சரி: ';
    maskedIdxs.forEach(function(idx,i){ correctHtml += (currentKural.correct_words[String(idx)] || '') + (i<maskedIdxs.length-1? ', ':''); });
    $('#correct-word-display').text(correctHtml);
    
    // Results container is inline in the card; no separate container to show.
    
    // Show kural explanation
    if (currentKural.porul) {
        displayKuralExplanation(currentKural.porul);
    }
    
    // Show next button
    $('#next-kural-btn').show();
    
    // Submit score to server (send arrays)
    submitScore(userAnswers, machineAnswers, machineTimeMs, userCorrectAll, machineCorrectAll);

    gameState = 'results';
}

/** Select option tile for a masked index */
function selectOption(idxKey, choice, container, tileEl){
    selectedOptions[idxKey] = choice;
    // visually mark selection in container
    $(container).find('.option-tile').css({background:'#fff', color:'#000'});
    tileEl.css({background:'#2b7cff', color:'#fff'});
}

/**
 * Display kural explanation
 */
function displayKuralExplanation(porul) {
    var explanationHtml = '';
    
    if (porul.Muuvey) {
        explanationHtml += '<p><span> மு.வ : </span>' + porul.Muuvey + '</p>';
    }
    
    if (porul.salaman) {
        explanationHtml += '<p><span> சாலமன் பாப்பையா : </span>' + porul.salaman + '</p>';
    }
    
    $('#kural-vilakam-content').html(explanationHtml);
    $('#kural-vilakam-container').show();
}

/**
 * Submit score to server
 */
function submitScore(userAnswer, machinePrediction, machineTimeMs, userCorrect, machineCorrect) {
    // Build correct_words map from currentKural.correct_words if present
    var payload = {
        kural_id: currentKural.kural_id,
        correct_words: currentKural.correct_words || {},
        user_answer: userAnswer,
        machine_prediction: machinePrediction,
        user_time_ms: userTimeMs,
        machine_time_ms: machineTimeMs,
        user_correct: userCorrect,
        machine_correct: machineCorrect
    };

    $.ajax({
        url: '/ngram/submit_score',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        dataType: 'json',
        success: function(response) {
            console.log('Score submitted successfully');
            loadLeaderboard();
        },
        error: function(xhr, status, error) {
            console.error('Error submitting score:', error);
        }
    });
}

/**
 * Load and display leaderboard
 */
function loadLeaderboard() {
    $.ajax({
        url: '/ngram/leaderboard',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            displayLeaderboard(response.leaderboard || []);
        },
        error: function(xhr, status, error) {
            console.error('Error loading leaderboard:', error);
                    // show error message in the tbody without touching the table header
                    $('#leaderboard-body').html('<tr><td colspan="4" style="text-align: center; padding: 20px;">Leaderboard ஏற்றுவதில் பிழை</td></tr>');
        }
    });
}

/**
 * Display leaderboard data
 */
function displayLeaderboard(leaderboard) {
    // Build rows and inject into tbody to preserve the table header and layout
    var rowsHtml = '';

    if (!Array.isArray(leaderboard) || leaderboard.length === 0) {
        rowsHtml = '<tr><td colspan="4" style="text-align: center; padding: 20px;">இன்னும் எவரும் விளையாடவில்லை</td></tr>';
    } else {
        leaderboard.forEach(function(entry) {
            var avgTimeSeconds = '0.00';
            if (entry.avg_time_ms) {
                avgTimeSeconds = (entry.avg_time_ms / 1000).toFixed(2);
            }
            rowsHtml += '<tr>' +
                '<td class="rank" style="padding:8px 6px;">#' + (entry.rank || '') + '</td>' +
                '<td class="user-name" style="padding:8px 6px;">' + (entry.user_name || 'Anonymous') + '</td>' +
                '<td class="diamond-points" style="text-align:center; padding:8px 6px;">' + (entry.total_correct || 0) + '</td>' +
                '<td class="diamond-points" style="text-align:center; padding:8px 6px;">' + avgTimeSeconds + 's</td>' +
                '</tr>';
        });
    }

    $('#leaderboard-body').html(rowsHtml);
}

