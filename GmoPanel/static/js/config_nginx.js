$(document).ready(function() {
    $('#summernote_http').on('summernote.init', function () {
        $('#summernote_http').summernote('codeview.activate');
    }).summernote({
        height: 500,
        placeholder: 'Paste content here...',
        codemirror: {
            theme: 'monokai'
        },
        callbacks: {
            onInit: function() {
                $("div.note-editor .panel-heading").hide();
                $("div.note-editor .note-statusbar").hide();
                $("div.note-editor .note-status-output").hide();
                $('textarea.note-codable').attr("disabled","disabled");
                $('textarea.note-codable').css({"background-color": "white", "font-size": "10px","color": "#222"});
            }
        }
    });

    $('#summernote_https').on('summernote.init', function () {
        $('#summernote_https').summernote('codeview.activate');
    }).summernote({
        height: 500,
        placeholder: 'Paste content here...',
        codemirror: {
            theme: 'monokai'
        },
        callbacks: {
            onInit: function() {
                $("div.note-editor .panel-heading").hide();
                $("div.note-editor .note-statusbar").hide();
                $("div.note-editor .note-status-output").hide();
                $('textarea.note-codable').attr("disabled","disabled");
                $('textarea.note-codable').css({"background-color": "white", "font-size": "10px","color": "#222"});
            }
        }
    });
    $('html, body').animate({
        scrollTop: $("#demo2").offset().top
    }, 2000);
});

$(document).on('click','.container-ssl',function (event) {
    event.preventDefault();
    var input = $(this).children('input');
    var id = input.attr('id');
    if(id == "icheck-http"){
        var formName = "#config-ngnix-http";
    }else{
        var formName = "#config-ngnix-https";
    }
    if(input.is(':checked')){
        input.removeAttr("checked");
        $(formName).find('textarea.note-codable').attr("disabled","disabled");
        $(formName).next().attr("disabled","disabled");
    }else{
        input.attr("checked","checked");
        $(formName).find('textarea.note-codable').removeAttr("disabled");
        $(formName).next().removeAttr("disabled");
    }
});

$(document).on('click','.add-http',function (event) {
    event.preventDefault();
    var textareaValue = $('#summernote_http').summernote('code');
    $('#config-ngnix-http').find('textarea[name="config_content"]').val(textareaValue);
    var dataForm = $('#config-ngnix-http').serializeArray();
    $.ajax({
        url: "/cPanel/Settings/configNginx/",
        type: "POST",
        dataType: "json",
        data:dataForm,
        beforeSend:function(){
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        complete:function(){
            $('#loader').modal('hide');
        },
        success: function (result) {
            if (result.status) {
                autohidenotify2('success','top  right','Notification',result.msg,8000);
                $('#config-ngnix-http').find('textarea.note-codable').attr("disabled","disabled");
                $('#config-ngnix-http').next().attr("disabled","disabled");
                $('#icheck-http').removeAttr("checked");
            } else {
                autohidenotify2('error','top  right','Notification',result.msg,8000);
            }
        },
        error: function () {
            autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
        }
     });
});

$(document).on('click','.add-https',function (event) {
    event.preventDefault();
    var textareaValue = $('#summernote_https').summernote('code');
    $('#config-ngnix-https').find('textarea[name="config_content"]').val(textareaValue);
    var dataForm = $('#config-ngnix-https').serializeArray();
    $.ajax({
        url: "/cPanel/Settings/configNginx/",
        type: "POST",
        dataType: "json",
        data:dataForm,
        beforeSend:function(){
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        complete:function(){
            $('#loader').modal('hide');
        },
        success: function (result) {
            if (result.status) {
                autohidenotify2('success','top  right','Notification',result.msg,8000);
                $('#config-ngnix-https').find('textarea.note-codable').attr("disabled","disabled");
                $('#config-ngnix-https').next().attr("disabled","disabled");
                $('#icheck-ssl').removeAttr("checked");
            } else {
                autohidenotify2('error','top  right','Notification',result.msg,8000);
            }
        },
        error: function () {
            autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
        }
    });
});