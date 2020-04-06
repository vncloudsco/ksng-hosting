$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});
/**
 * Change WAF setting on/of
 */
$(document).on('click','.btn-change',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let status = ($(this).attr('status') != '') ? $(this).attr('status') : '';
    let url = '/securitys/changeStatus/'+myId;
    let method = 'POST';
    let thisBtn = $(this);
    $('.tooltip ').hide();
    $('.notifyjs-wrapper').remove();

    if (status == 1) {
        nconfirm2('Notification','Are you sure about turning on WAF on this website?');
    } else if (status == 0) {
        nconfirm2('Notification','Are you sure about turning off WAF on this website?');
    }else{
        autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
    }
    
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $('.notifyjs-wrapper').remove();
        if(myId != '' && status != ''){
            $.ajax({
                url: url,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                type: method,
                data: {
                    status: status,
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
                            $('#on-off-pos').text('on');
                        }else if(status == 0){
                            thisBtn.removeClass('bg-grey');
                            thisBtn.parent().find('.btn-primary').addClass("bg-grey");
                            thisBtn.attr("title","Currently turned off");
                            thisBtn.parent().find('.btn-primary').attr("title", "Click to turn on");
                            thisBtn.parent().find('.btn-primary').attr("disabled", false);
                            $('#on-off-pos').text('off');
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

/**
 * load restrict access by authentication list
 */
function loadReba(){
    let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
    let url = '/securitys/listReba/'+provisionId;
    let method = 'POST';
    if(provisionId != ''){
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            dataType: "text",
            beforeSend: function(){
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete:function(){
                $('#loader').modal('hide');
            },
            success: function(result) {
                $('#list-reba').html(result);
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top  right','Notification',error,8000);
            }
        });
    }else{
        return false;
    }   
}

/**START RESTRICT ACCESS BY AUTHENTICATION */
$(document).ready(function () {
    /**
     * Click to restrict access by authentication tab
     */
    $('#reba-tab').click(function (e) { 
        e.preventDefault();
        $('#logWafShow').hide();
        var hasClass = $(this).hasClass('active');
        if(!hasClass){
            loadReba();
        }
    });

    /**
     * Save restrict access by authentication configuration
     */
    $('#btn-save-reba').click(function (e) { 
        e.preventDefault();
        
        jQuery.validator.addMethod("reba_username", function(value, element) {
            if (/^[0-9a-zA-z.]+$/.test(value)) {
                return true;   // PASS validation when REGEX matches
            } else {
                return false;  // FAIL validation
            };
        }, 'Username must be in a->z, A->Z or 0->9');
        jQuery.validator.addMethod("reba_password", function(value, element) {
            if (/^[0-9A-za-z!@#$%^&*()-_.]+$/.test(value)) {
                return true;   // PASS validation when REGEX matches
            } else {
                return false;  // FAIL validation
            };
        }, 'Password must be in a->z, A->Z, 0->9 or special characters');
        jQuery.validator.addMethod("reba_url", function(value, element) {
            var pattern = new RegExp('^(\\:\\d+)?(\[-a-z\\d%_.~+]*)*'+ // port and path
                '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
                '(\\#[-a-z\\d_]*)?$','i');
            if (pattern.test(value)) {
                return true;   // PASS validation when REGEX matches
            } else {
                return false;  // FAIL validation
            };
        }, 'The URL is malformed! (example : wp-admin)');
        $('#reba-save-form').validate({
            rules: {
                url:{
                    reba_url : true
                },
                user:{
                    reba_username: true,
                    minlength: 4,
                    maxlength:32
                },
                password:{
                    reba_password: false,
                    minlength: 4,
                    maxlength:32
                }
            }
        });

        let validationResult = $('#reba-save-form').valid();

        if(validationResult){
            let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
            let dataForm = $('#reba-save-form').serializeArray();
            let url = "/securitys/saveReba/"+provisionId;
            let method = 'POST';
            $.ajax({
                url: url,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                type: method,
                data: dataForm,
                dataType: 'json',
                beforeSend: function(){
                    $('#btn-save-reba').button('loading');
                },
                complete: function(){
                    $('#btn-save-reba').button('reset');
                },
                success: function(result) {
                    if(result.status){
                        autohidenotify2('success','top right','Notification','Create new configuration successfully.',8000);
                        $('#reset-form-reba').click();
                        $('#close-reba-modal').click();
                        loadReba();
                    }else{
                        autohidenotify2('error','top right','Notification',result.msg,8000);
                    }
                },
                error: function() {
                    autohidenotify2('error','top right','Notification',error,8000);
                }
            });
        }
    });
});

$(document).on('click','.btn-delete-reba',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let url = '/securitys/deleteReba/'+myId;
    let method = 'GET';
    $('.tooltip ').hide();
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about deleting this configuation?');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $('.notifyjs-wrapper').remove();
        if(myId != ''){
            $.ajax({
                url: url,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                type: method,
                data: {},
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
                        autohidenotify2('success','top  right','Notification',result.msg,8000);   
                        loadReba();
                    }else if(status == 0){
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

$(document).on('click','.change-password-btn',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
    let url = '/securitys/getChangePassword/'+myId;
    let method = 'POST';
    $('#change-pass-pos').html('');
    if(myId != '' && provisionId != ''){
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                provision_id: provisionId,
                reba_id: myId
            },
            dataType: "text",
            beforeSend: function(){
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete:function(){
                $('#loader').modal('hide');
            },
            success: function(result) {
                $('#change-pass-pos').html(result);
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top  right','Notification',error,8000);
            }
        });
    }else{
        autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
    }
});

$(document).on('click','#save-new-password-btn',function (event) {
    event.preventDefault();
        
    jQuery.validator.addMethod("reba_password", function(value, element) {
        if (/^[0-9A-za-z!@#$%^&*()-_.]+$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Password must be in a->z, A->Z, 0->9 or special characters');

    $('#reba-edit-form').validate({
        rules: {
            password:{
                reba_password: false,
                minlength:4,
                maxlength:32
            }
        }
    });

    let validationResult = $('#reba-edit-form').valid();

    if(validationResult){
        let newPassword = ($('#new-password').val() != '') ? $('#new-password').val() : '';
        let configId = ($('#config-id').val() != '') ? $('#config-id').val() : '';
        let url = "/securitys/changePassword/"+configId;
        let method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                new_password: newPassword,
            },
            dataType: 'json',
            beforeSend: function(){
                $('#save-new-password-btn').button('loading');
            },
            complete: function(){
                $('#save-new-password-btn').button('reset');
            },
            success: function(result) {
                if(result.status){
                    autohidenotify2('success','top right','Notification',result.msg,8000);
                    $('#reset-form-edit-reba').click();
                    $('#close-edit-reba-modal').click();
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                }
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top right','Notification',error,8000);
            }
        });
    }
});


function loadRebi(){
    let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
    let url = '/securitys/listRebi/'+provisionId;
    let method = 'POST';
    if(provisionId != ''){
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            dataType: "text",
            beforeSend: function(){
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete:function(){
                $('#loader').modal('hide');
            },
            success: function(result) {
                $('#list-rebi').html(result);
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top  right','Notification',error,8000);
            }
        });
    }else{
        return false;
    }   
}
/**START RESTRICT ACCESS BY IP FILTER */
$(document).ready(function () {
    /**
     * Click to restrict access by ip filter tab
     */
    $('#rebi-tab').click(function (e) { 
        e.preventDefault();
        $('#logWafShow').hide();
        var hasClass = $(this).hasClass('active');
        if(!hasClass){
            loadRebi();
        }
    });

    /**
     * Save restrict access by authentication configuration
     */
    $('#btn-save-rebi').click(function (e) { 
        e.preventDefault();
        $('#rebi-save-form').validate({
            
        });

        let validationResult = $('#rebi-save-form').valid();

        if(validationResult){
            let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
            let dataForm = $('#rebi-save-form').serializeArray();
            let url = "/securitys/saveRebi/"+provisionId;
            let method = 'POST';
            $.ajax({
                url: url,
                type: method,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                data: dataForm,
                dataType: 'json',
                beforeSend: function(){
                    $('#btn-save-rebi').button('loading');
                },
                complete: function(){
                    $('#btn-save-rebi').button('reset');
                },
                success: function(result) {
                    if(result.status){
                        autohidenotify2('success','top right','Notification','Create new configuration successfully.',8000);
                        $('#reset-form-rebi').click();
                        $('#close-rebi-modal').click();
                        loadRebi();
                    }else{
                        autohidenotify2('error','top right','Notification',result.msg,8000);
                    }
                },
                error: function(xhr, textStatus, error) {
                    autohidenotify2('error','top right','Notification',error,8000);
                }
            });
        }
    });
});

$(document).on('click','.btn-delete-rebi',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let url = '/securitys/deleteRebi/'+myId;
    let method = 'POST';
    $('.tooltip ').hide();
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about deleting this configuation?');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $('.notifyjs-wrapper').remove();
        if(myId != ''){
            $.ajax({
                url: url,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                type: method,
                data: {},
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
                        autohidenotify2('success','top  right','Notification',result.msg,8000);   
                        loadRebi();
                    }else if(status == 0){
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

$(document).on('click','.change-ip-btn',function (event) {
    let myId = ($(this).attr('myId') != '') ? $(this).attr('myId') : '';
    let provisionId = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
    let url = '/securitys/getChangeIp/'+myId;
    let method = 'POST';
    $('#change-ip-pos').html('');
    if(myId != '' && provisionId != ''){
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                provision_id: provisionId,
            },
            dataType: "text",
            beforeSend: function(){
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete:function(){
                $('#loader').modal('hide');
            },
            success: function(result) {
                $('#change-ip-pos').html(result);
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top  right','Notification',error,8000);
            }
        });
    }else{
        autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
    }
});

$(document).on('click','#save-new-ip-btn',function (event) {
    event.preventDefault();
    $('#rebi-edit-form').validate({
        
    });

    let validationResult = $('#rebi-edit-form').valid();

    if(validationResult){
        let newIp = ($('#new-ip').val() != '') ? $('#new-ip').val() : '';
        let configId = ($('#config-id').val() != '') ? $('#config-id').val() : '';
        let url = "/securitys/changeIp/"+configId;
        let method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                new_ip: newIp,
                config_id: configId
            },
            dataType: 'json',
            beforeSend: function(){
                $('#save-new-ip-btn').button('loading');
            },
            complete: function(){
                $('#save-new-ip-btn').button('reset');
            },
            success: function(result) {
                if(result.status){
                    autohidenotify2('success','top right','Notification',result.msg,8000);
                    $('#reset-form-edit-rebi').click();
                    $('#close-edit-rebi-modal').click();
                    loadRebi()
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                }
            },
            error: function(xhr, textStatus, error) {
                autohidenotify2('error','top right','Notification',error,8000);
            }
        });
    }
});

$(document).on('click','#waf-tab',function(){
    $('#logWafShow').show();
});