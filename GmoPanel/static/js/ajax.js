$(document).on('click','#btnResetPassword',function (event) {
    event.preventDefault();
    var username = ($('#username').val() != '') ? $('#username').val() : '';
    var email 	 = ($('#email').val() != '') ? $('#email').val() : '';
    if(username == '' || email == ''){
        autohidenotify2('error','top right','Notification','Username and email cannot be null and must match to each other.',8000);
    }else{
        var dataForm = $('#resetPassword').serializeArray();
        var url = "/cPanel/accounts/sendResetEmail";
        var method = 'POST';
        $.ajax({
            url: url,
            type: method,
            data: dataForm,
            dataType: "json",
            beforeSend: function(){
                $('#btnResetPassword').button('loading');
            },
            complete: function(){
                $('#btnResetPassword').button('reset');
            },
            success: function(result) {
                if(result.status == 1){
                    $('#reset_form').click();
                    autohidenotify2('success','top right','Notification',result.msg,8000);
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                }
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top right','Notification','Can not forgot password!Please try laster aign!',8000);
            }
        });
    }
})

//SSL Installer
$(document).on('click','#install-ssl-btn',function (event) {
    event.preventDefault();
    var domain_name = ($('#domain_name').val() != '') ? $('#domain_name').val() : '';
    var url = '/cPanel/SslInstaller/install';
    var method = 'POST';
    $.ajax({
        url: url,
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: method,
        data: {
            domain_name: domain_name,
        },
        dataType: "json",
        beforeSend: function(){
            $('#install-ssl-btn').button('loading');
        },
        success: function(result) {
            if(result.status == 1){
                autohidenotify2('success','top  right','Notification',result.msg,8000);
            }else{
                autohidenotify2('error','top  right','Notification',result.msg,8000);
            }
            
            $('#install-ssl-btn').button('reset');
        },
        error: function(xhr, textStatus, error) {
            $('#install-ssl-btn').button('reset');
        }
    });
});