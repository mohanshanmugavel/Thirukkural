//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

function highlightKuralWords(wordStatuses) {
    console.log("Word statuses from speech API:", wordStatuses);
    var wordElements = document.querySelectorAll(".kural-word");
    if (!wordElements || wordElements.length === 0) return;
    
    // Reset classes
    wordElements.forEach(function(el) {
        el.classList.remove("word-correct", "word-wrong", "word-missing");
    });

    // Apply new classes based on index
    wordStatuses.forEach(function(statusObj, index) {
        var el = document.querySelector(`.kural-word[data-index="${index}"]`);
        if (el) {
            el.classList.add("word-" + statusObj.status);
        }
    });
}

function playSuccessSound() {
    try {
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        var now = ctx.currentTime;
        
        function playTone(freq, time, duration) {
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, time);
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            gain.gain.setValueAtTime(0.3, time);
            gain.gain.exponentialRampToValueAtTime(0.01, time + duration);
            
            osc.start(time);
            osc.stop(time + duration);
        }
        
        playTone(523.25, now, 0.15);       // C5
        playTone(659.25, now + 0.1, 0.15);  // E5
        playTone(783.99, now + 0.2, 0.15);  // G5
        playTone(1046.50, now + 0.3, 0.4);  // C6
    } catch(e) {
        console.error("Failed to play success sound:", e);
    }
}


var gumStream;                      //stream from getUserMedia()
var rec;                            //Recorder.js object
var input;                          //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

function startRecording() {
    console.log("recordButton clicked");

    /*
        Simple constraints object, for more advanced audio features see
        https://addpipe.com/blog/audio-constraints-getusermedia/
    */

    var constraints = { audio: true, video: false }

    /*
        Disable the record button until we get a success or fail from getUserMedia() 
    */

    recordButton.disabled = true;
    stopButton.disabled = false;
    pauseButton.disabled = false

    /*
        We're using the standard promise based getUserMedia() 
        https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    */

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        /*
            create an audio context after getUserMedia is called
            sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
            the sampleRate defaults to the one set in your OS for your playback device

        */
        audioContext = new AudioContext();

        //update the format 
        // document.getElementById("formats").innerHTML="Format: 1 channel pcm @ "+audioContext.sampleRate/1000+"kHz"

        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        /* 
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */
        rec = new Recorder(input, { numChannels: 1 })
        rec.mimeType = 'audio/wav';
        //start the recording process
        rec.record()

        console.log("Recording started");

    }).catch(function (err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
        pauseButton.disabled = true
    });
}

function pauseRecording() {
    console.log("pauseButton clicked rec.recording=", rec.recording);
    if (rec.recording) {
        //pause
        rec.stop();
        pauseButton.innerHTML = 'RESUME <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="M6.271 5.055a.5.5 0 0 1 .52.038l3.5 2.5a.5.5 0 0 1 0 .814l-3.5 2.5A.5.5 0 0 1 6 10.5v-5a.5.5 0 0 1 .271-.445z"/></svg>';
    } else {
        //resume
        rec.record()
        pauseButton.innerHTML = 'PAUSE <svg class="audio-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" /><path d="M5 6.25a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0v-3.5zm3.5 0a1.25 1.25 0 1 1 2.5 0v3.5a1.25 1.25 0 1 1-2.5 0v-3.5z" /></svg>';
    }
}

function stopRecording() {
    console.log("stopButton clicked");

    //disable the stop button, enable the record too allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;
    pauseButton.disabled = true;

    //reset button just in case the recording is stopped while paused
    pauseButton.innerHTML = "Pause";

    //tell the recorder to stop the recording
    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {

    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    li.className = 'recorded-audio';
    // var link = document.createElement('a');

    //name of .wav file to use during upload and download (without extendion)
    var filename = new Date().toISOString();

    //add controls to the <audio> element
    au.controls = true;
    au.src = url;
    au.id = "kural-audio-file";

    //save to disk link
    // link.href = url;
    // link.download = filename+".wav"; //download forces the browser to donwload the file using the  filename
    // link.innerHTML = "Save to disk";

    //add the new audio element to li
    li.appendChild(au);

    // //add the filename to the li
    // li.appendChild(document.createTextNode(filename+".wav "))

    // //add the save to disk link to li
    // li.appendChild(link);
    //upload link
    var upload = document.createElement('button');
    upload.className = 'submit-audio';
    upload.innerHTML = 'சமர்ப்பி <svg class="audio-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16"><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z" /><path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z" /></svg>';
    upload.addEventListener("click", function (event) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function (e) {
            if (this.readyState === 4) {
                var response = e.target.responseText;
                console.log("Server response:", response);
                try {
                    var data = JSON.parse(response.trim());
                    
                    // Highlight Words based on strict left-to-right matching
                    highlightKuralWords(data.word_statuses);
                    
                    // Update Result Card UI
                    document.getElementById('resultCard').style.display = 'block';
                    document.getElementById('bottomActions').style.display = 'grid';

                    var controlsEl = document.getElementById('controls');
                    if (controlsEl) controlsEl.style.display = 'none';
                    var recordingsList = document.getElementById('recordingsList');
                    if (recordingsList) recordingsList.style.display = 'none';
                    var vilakamEl = document.querySelector('.kural-vilakam-container');
                    if (vilakamEl) vilakamEl.style.display = 'none';
                    
                    document.getElementById('accuracyText').innerText = data.accuracy + "%";
                    document.getElementById('accuracyBar').style.width = data.accuracy + "%";
                    document.getElementById('scoreText').innerText = data.count + " / " + data.total;
                    
                    var wrongWordsContainer = document.getElementById('wrongWordsContainer');
                    var wrongWordsList = document.getElementById('wrongWordsList');
                    wrongWordsList.innerHTML = '';
                    if (data.wrong_words && data.wrong_words.length > 0) {
                        wrongWordsContainer.style.display = 'block';
                        document.getElementById('wrongCount').innerText = data.wrong_words.length;
                        data.wrong_words.forEach(function(w) {
                            var li = document.createElement('li');
                            li.innerHTML = `<strong>எதிர்பார்த்தது:</strong> ${w.expected} <br><strong>நீங்கள் கூறியது:</strong> ${w.said || '<em>(எதுவுமில்லை)</em>'}`;
                            wrongWordsList.appendChild(li);
                        });
                    } else {
                        wrongWordsContainer.style.display = 'none';
                        document.getElementById('wrongCount').innerText = "0";
                    }

                    var missingWordsContainer = document.getElementById('missingWordsContainer');
                    var missingWordsList = document.getElementById('missingWordsList');
                    missingWordsList.innerHTML = '';
                    if (data.missing_words && data.missing_words.length > 0) {
                        missingWordsContainer.style.display = 'block';
                        document.getElementById('missingCount').innerText = data.missing_words.length;
                        data.missing_words.forEach(function(w) {
                            var li = document.createElement('li');
                            li.innerText = w;
                            missingWordsList.appendChild(li);
                        });
                    } else {
                        missingWordsContainer.style.display = 'none';
                        document.getElementById('missingCount').innerText = "0";
                    }

                    var extraWordsContainer = document.getElementById('extraWordsContainer');
                    var extraWordsList = document.getElementById('extraWordsList');
                    extraWordsList.innerHTML = '';
                    if (data.extra_words && data.extra_words.length > 0) {
                        extraWordsContainer.style.display = 'block';
                        document.getElementById('extraCount').innerText = data.extra_words.length;
                        data.extra_words.forEach(function(w) {
                            var li = document.createElement('li');
                            li.innerText = w;
                            extraWordsList.appendChild(li);
                        });
                    } else {
                        extraWordsContainer.style.display = 'none';
                        document.getElementById('extraCount').innerText = "0";
                    }

                    // Perfect Score Check
                    if (data.accuracy === 100) {
                        playSuccessSound();
                        var confe = document.querySelector('#my-canvas');
                        if (confe) confe.classList.add('active');
                        var confettiSettings = { target: 'my-canvas' };
                        var confetti = new ConfettiGenerator(confettiSettings);
                        confetti.render();
                    }
                } catch (err) {
                    console.error("Failed to parse JSON response or update UI:", err);
                }
                
                if (document.getElementById('kural-audio-file')) {
                    document.getElementById('kural-audio-file').style.display = 'none';
                }
            }
        };
        var fd = new FormData();
        fd.append("audio_data", blob, filename);
        fd.append("getKuralId", document.getElementById('kuralId').value)
        xhr.open("POST", "/transaltee", true);
        xhr.send(fd);
    })
    li.appendChild(upload)//add the upload link to li

    //add the li element to the ol
    recordingsList.innerHTML = '';
    recordingsList.appendChild(li);
}



// openPopup removed as Result Card replaces it