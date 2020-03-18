$(document).ready(function() {
    $('#reset-pass-sftp').click(function(event) {
        var url = "/cPanel/SshConnector/resetPassword";
        var method = 'POST';

        $.ajax({
            url: url,
            headers : {
                'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
            },
            type: method,
            data: {
            },
            beforeSend: function(){
                
            },
            success: function(result) {
                var data = JSON.parse(result);
                if(data.status == 1){
                    autohidenotify2('success','top right','Notification','SFTP password is changed successfully.',4000);
                    $('#password_pos').hide().html(data.msg).fadeIn('slow');
                }else{
                    autohidenotify2('error','top right','Notification',data.msg,4000);
                }
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top right','Notification',error,4000);
            }
        });
    });
});