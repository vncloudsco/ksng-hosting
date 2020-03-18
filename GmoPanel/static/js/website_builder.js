$('.active_theme').click(function(event) {
    var theme_id = $(this).attr('myId');
    $('#theme_id').val(theme_id);
    $("#result_zone").empty().removeClass('alert alert-info alert-dismissable');
});

$('#delete_all_wb').click(function(event) {
    var theme_id = ($('#theme_id').val() != '') ? $('#theme_id').val() : '';
    var id = ($('#domain_id').val() != '') ? $('#domain_id').val() : '';
    
    if(theme_id == ''){
        autohidenotify2('error','top right','Notification','Invalid theme. Please reload your web page and try again.',4000);
    }else{
        var url = "/websites/activeTheme/";
        var method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                theme_id: theme_id,
                id: id,
            },
            dataType: "json",
            beforeSend: function(){
                $('#delete_all_wb').button('loading');
            },
            complete: function(){
                $('#delete_all_wb').button('reset');
            },
            success: function(result) {
                if(result.status == 1){
                    var content = result.msg;
                    $('#result_zone').hide().html(content).addClass('alert alert-info alert-dismissable').fadeIn('slow');
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,4000);
                }
            },
            error: function(xhr, textStatus, error) {
                notify('error','top right','There is an error occurred when changing theme.');
            }
        });
    }
});


$('#keep_all_wb').click(function(event) {
    var theme_id = ($('#theme_id').val() != '') ? $('#theme_id').val() : '';
    var domain = ($('#domain').val() != '') ? $('#domain').val() : '';

    if(theme_id == ''){
        autohidenotify2('error','top right','Notification','Invalid theme. Please reload your web page and try again.',4000);
    }else{
        var url = "/websites/changeTheme/";
        var method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                theme_id: theme_id,
                domain: domain,
            },
            dataType: "json",
            beforeSend: function(){
                $('#keep_all_wb').button('loading');
            },
            complete: function(){
                $('#keep_all_wb').button('reset');
            },
            success: function(result) {
                if(result.status == 1){
                    autohidenotify2('success','top right','Notification','Your website is created successfully.',4000);
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,4000);
                }
            },
            error: function(xhr, textStatus, error) {
                notify('error','top right','There is an error occurred when changing theme.');
            }
        });
    }
});