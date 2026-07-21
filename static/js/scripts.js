$("form[name=signup_form").submit(function (e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/user/signup",
        type: "POST",
        data: data,
        dataType: "json",
        success: function (resp) {
            window.location.href = "/index/";
        },
        error: function (resp) {
            $error.text(resp.responseJSON.error).removeClass("error--hidden");
            console.log(resp);
        }
    });
    e.preventDefault();
});


$("form[name=login_form").submit(function (e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();

    $.ajax({
        url: "/user/login",
        type: "POST",
        data: data,
        dataType: "json",
        success: function (resp) {
            window.location.href = "/index/";
        },
        error: function (resp) {
            $error.text(resp.responseJSON.error).removeClass("error--hidden");
        }
    });
    e.preventDefault();
});



$("form[name=adhigaram_filter_form").submit(function (e) {
    var $form = $(this);
    var data = $form.serialize();


    $.ajax({
        url: "/filter_adhigaram",
        type: "POST",
        data: data,
        dataType: "json",
        success: function (response) {
            // console.log(response['adhigaram_id']);
            adhigaram_id = response['adhigaram_id'];

            for (let kuralId = 1; kuralId < 11; kuralId++) {
                var select_kural = document.getElementById("select-kural-" + kuralId);
                var kural = document.getElementById("kural-" + kuralId);
                var kural_number = ((adhigaram_id - 1) * 10) + kuralId;
                kural.innerHTML = kural_number
                select_kural.href = "learn_thirukkural?kuralId=" + kural_number;
            }
        },
    })
    e.preventDefault();
});


$("form[name=adhigaram_game_form").submit(function (e) {
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    
    // Check if ngram game is selected
    var gameType = $form.find('input[name="game_type"]:checked').val();
    if (gameType === "/ngram/game") {
        // Directly redirect to ngram game (doesn't need kuralId)
        window.location.href = "/ngram/game";
        e.preventDefault();
        return;
    }

    $.ajax({
        url: "/selected_game",
        type: "POST",
        data: data,
        dataType: "json",
        success: function (resp) {
            window.location.href = resp.site+"?kuralId="+resp.kuralId;
        },
        error: function (resp) {
            $error.text(resp.responseJSON.error);
        }
    });
    e.preventDefault();
});


