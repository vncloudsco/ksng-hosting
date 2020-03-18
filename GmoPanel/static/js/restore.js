function loadDomain(domain){
    var url = "/cPanel/Restore/listDomain";
    var method = 'POST';

    var loading = '<tr><td colspan="7" id="loading-zone"><div class="lds-css ng-scope"><div style="width:100% !important;height:100%" class="lds-facebook"><div></div><div></div><div></div></div></div></td></tr>';
    
    $.ajax({
        url: url,
        headers : {
            'X-CSRF-Token': $('#form-list-domain').find('input[name="_csrfToken"]').val()
        },
        type: method,
        data: {
            domain: domain
        },
        beforeSend: function(){
            $('#domain_list').html(loading);
        },
        success: function(result) {
            $('#domain_list').hide().html(result).fadeIn('slow');
        },
        error: function(xhr, textStatus, error) {
            // alert(error);
            autohidenotify2('error','top right','Notification',error,4000);
        }
    });
}

$(document).ready(function() {
    $('#search_btn').click(function(event) {
        var domain = ($('#domain_lookup').val() != null) ? $('#domain_lookup').val() : null;
        if(domain == null){
            autohidenotify2('error','top right','Notification','The selected domain is invalid.',4000);
        }else{
            loadDomain(domain);
        }
    });
});

$(function(){
    $(document).on('click', '.notifyjs-metro-base .d_no', function() {
        $(this).trigger('notify-hide');
    });
})

$(document).on('click','.restore-btn',function (event) {
    var myId = ($(this).attr('myId') != null) ? $(this).attr('myId') : null;
    var backup = $(this).parents('tr').find('td').eq(3).find('select.backup-ver').val();

    $(this).button('loading');
    if(backup == ''){
        autohidenotify2('error','top right','Notification','Backup version can not be empty.',8000);
    }else{
        var url = "/cPanel/Restore/restore";
        var method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRF-Token': $('#form-list-domain').find('input[name="_csrfToken"]').val()
            },
            type: method,
            data: {
                myId: myId,
                backup: backup
            },
            beforeSend: function(){
            },
            success: function(result) {
                var data = JSON.parse(result);
                if(data.status == 1){
                    autohidenotify2('success','top right','Notification','Restoring website is completed successfully!',8000);
                }else{
                    autohidenotify2('error','top right','Notification',data.msg,8000);
                }
                $('.restore-btn').button('reset');
            },
            error: function(xhr, textStatus, error) {
                $('.restore-btn').button('reset');
            }
        });
    }
});