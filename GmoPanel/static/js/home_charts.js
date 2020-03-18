$(function () {
    $(".knob").knob();
    setInterval(function(){ loadChart(); }, 3000);
});

function loadChart() {
    $.ajax({
        url: "/load_chart",
        headers : {
            'X-CSRF-Token': getCookie('csrftoken')
        },
        type: "GET",
        dataType: "html",
        beforeSend:function(){
            //before send
        },
        complete:function(){
            //complete
        },
        success: function (result) {
            $('#show_chart').html(result)
            $(".knob").knob();
        },
        error: function () {

        }
    });
}
