//dashboard
function loadStats() {
    var progressBar = document.getElementById("progress");
    var completedKuralCount = document.getElementById("completed-kural");
    var streak = document.getElementById("streak-value");
    var streakValue = streak ? (parseInt(streak.innerText) || 0) : 0;
    var completedKural = completedKuralCount ? (parseInt(completedKuralCount.innerText) || 0) : 0;
    var progressVal = (completedKural % 10) || 0;
    if (progressBar) {
        progressBar.style.width = (progressVal * 10) + '%';
        progressBar.innerHTML = (progressVal * 10) + '%';
    }
}


function loadData(type, data, time) {
    var width = 1;
    var setData = setInterval(load, time);
    function load() {
        if (width >= data) {
            clearInterval(setData);
        } else {
            width++;
            type.style.width = width * 10 + '%';
            type.innerHTML = width * 1;
        }
    }
}

//Drag and drop game


function dragStart(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function allowDrop(event) {
    event.preventDefault();
}

function drop(event) {
    event.preventDefault();
    var data = event.dataTransfer.getData("text");
    event.target.appendChild(document.getElementById(data));
    var wordid="word"+event.target.id;
    document.getElementById(wordid).value=data;
}
