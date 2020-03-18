$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});

$(document).ready(function(){
    $('.show-cache').click(function (e) { 
        event.preventDefault();
        let id = $(this).data('id');
        let type = $(this).data('type');
        let url = "CacheManager/showCache";
        let method = 'POST';
        let td = $(this).parents('td');
        let thisBtn = $(this);
        $('.tooltip ').hide();
        $.ajax({
            url: url,
            headers : {
                'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
            },
            type: method,
            data: {
                myId: id,
                type: type,
            },
            dataType: 'json',
            beforeSend: function(){
                thisBtn.button('loading');
            },
            complete:function(){
                thisBtn.button('reset');
            },
            success: function(result) {
                if(result.status){
                    td.html(result.msg);
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                }
            },
            error: function() {
                notify('error','top right','There is an error occurred while getting php version.');
            }
        });
    });
});

$(document).on('click','.btn-clear-cache',function (event) {
    event.preventDefault();
    let type = ($(this).data('type') != '') ? $(this).data('type') : '';
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let thisBtn = $(this);
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about clearing cache this website?');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $('.notifyjs-wrapper').remove();
        if(type != '' && myId != ''){
            $.ajax({
                url: "/cPanel/CacheManager/clearCache",
                headers : {
                    'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
                },
                type: "POST",
                data: {
                    myId: myId,
                    type: type,
                },
                dataType: "json",
                beforeSend:function(){
                    thisBtn.button('loading');
                },
                complete:function(){
                    thisBtn.button('reset');
                },
                success: function (result) {
                    if(result.status){
                        autohidenotify2('success','top right','Notification','Clear cache website successfully!',8000);
                    }else{
                        autohidenotify2('error','top right','Notification',result.msg,8000);
                    }
                },
                error: function () {
                    autohidenotify2('error','top right','Notification','An error occured. Please try again.',8000);
                }
            });
        }else{
            autohidenotify2('error','top right','Notification','An error occured. Please try again.',8000);
        }
    });
});

$(document).on('click','.btn-change',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let type = ($(this).attr('type') != '') ? $(this).attr('type') : '';
    let status = ($(this).attr('status') != '') ? $(this).attr('status') : '';
    let url = '/cPanel/CacheManager/changeStatus';
    let method = 'POST';
    let thisBtn = $(this);
    $('.tooltip ').hide();
    $('.notifyjs-wrapper').remove();

    if (status == 1) {
        nconfirm2('Notification','Are you sure about turning on cache on this website?');
    } else if (status == 0) {
        nconfirm2('Notification','Are you sure about turning off cache on this website?');
    }else{
        autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
    }
    
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $('.notifyjs-wrapper').remove();
        if(type != '' && myId != '' && status != ''){
            $.ajax({
                url: url,
                headers : {
                    'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
                },
                type: method,
                data: {
                    myId: myId,
                    status: status,
                    type: type
                },
                dataType: "json",
                beforeSend: function(){
                    $('#loader').modal({backdrop: 'static', keyboard: false});
                    $('#loader').modal('show');
                },
                complete:function(){
                    $('#loader').modal('hide');
                },
                success: function(result) {
                    if(result.status == 1){
                        thisBtn.attr("disabled", true);
                        if(status == 1){
                            thisBtn.removeClass('bg-grey');
                            thisBtn.parent().find('.btn-danger').addClass('bg-grey');
                            thisBtn.attr("title","Currently turned on");
                            thisBtn.parent().find('.btn-danger').attr("title", "Click to turn off");
                            thisBtn.parent().find('.btn-danger').attr("disabled", false);
                        }else if(status == 0){
                            thisBtn.removeClass('bg-grey');
                            thisBtn.parent().find('.btn-primary').addClass("bg-grey");
                            thisBtn.attr("title","Currently turned off");
                            thisBtn.parent().find('.btn-primary').attr("title", "Click to turn on");
                            thisBtn.parent().find('.btn-primary').attr("disabled", false);
                        }
                        autohidenotify2('success','top  right','Notification',result.msg,8000);
                    }else{
                        autohidenotify2('error','top  right','Notification',result.msg,8000);
                    }
                },
                error: function(xhr, textStatus, error) {
                    autohidenotify2('error','top  right','Notification',error,8000);
                }
            });
        }else{
            autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
        }
    });   
});