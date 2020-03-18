$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});

$(document).ready(function () {
    $('#change-php-btn').click(function (e) { 
        e.preventDefault();
        $('.notifyjs-wrapper').remove();
        nconfirm2('Notification','Do you want to change php version?');

        let phpVer = $('#php-ver').val() ? $('#php-ver').val() : '';
        $('.notifyjs-metro-base .d_yes').click(function(event) {
            event.preventDefault();
            $(this).trigger('notify-hide');
            let url = "/cPanel/Settings/changePhp";
            let method = 'POST';
            $.ajax({
                url: url,
                headers : {
                    'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
                },
                type: method,
                data: {
                    phpVer: phpVer,
                },
                dataType: "json",
                beforeSend: function(){
                    $('.notifyjs-wrapper').remove();
                    $('#loader').modal({backdrop: 'static', keyboard: false});
                    $('#loader').modal('show');
                },
                complete:function(){
                    $('#loader').modal('hide');
                },
                success: function(result) {
                    if(result.status == 1){
                        let textPhpVer = '';
                        switch (phpVer) {
                            case 'php53': textPhpVer = 'Current vesion: PHP 5.3'; break;
                            case 'php': textPhpVer = 'Current vesion: PHP 5.6'; break;
                            case 'php70': textPhpVer = 'Current vesion: PHP 7.0'; break;
                            case 'php71': textPhpVer = 'Current vesion: PHP 7.1'; break;
                            case 'php72': textPhpVer = 'Current vesion: PHP 7.2'; break;
                            default: textPhpVer = 'Unknown'; break;
                        }
                        $('#current-pos').text(textPhpVer);
                        autohidenotify2('success','top right','Notification','Changing php version is completed successfully!',8000);
                    }else{
                        autohidenotify2('error','top right','Notification',result.msg,8000);
                    }
                },
                error: function() {
                    notify('error','top right','There is an error occurred while changing php version.');
                }
            });
        });
    });

    $('#restart-php-btn').click(function (e) { 
        e.preventDefault();
        $('.notifyjs-wrapper').remove();
        nconfirm2('Notification','Do you want to restart PHP?');

        $('.notifyjs-metro-base .d_yes').click(function(event) {
            event.preventDefault();
            $(this).trigger('notify-hide');
            let url = "/cPanel/Settings/restartPhp";
            let method = 'POST';
            $.ajax({
                url: url,
                headers : {
                    'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
                },
                type: method,
                data: {
                    
                },
                dataType: "json",
                beforeSend: function(){
                    $('.notifyjs-wrapper').remove();
                    $('#loader').modal({backdrop: 'static', keyboard: false});
                    $('#loader').modal('show');
                },
                complete:function(){
                    $('#loader').modal('hide');
                },
                success: function(result) {
                    if(result.status == 1){
                        autohidenotify2('success','top right','Notification','Restarting PHP is completed successfully!',8000);
                    }else{
                        autohidenotify2('error','top right','Notification',result.msg,8000);
                    }
                },
                error: function() {
                    notify('error','top right','There is an error occurred while restarting PHP.');
                }
            });
        });
    });
});