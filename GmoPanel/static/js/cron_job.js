$(document).ready(function () {
    $.each($('input[name="backup_type"]:checked'), function( key, value ) {
        if($(this).val() == 2) {
            $(this).parents('.cron-form').find('.ssh_config').show();
            $(this).parents('.cron-form').find('.ssh_config').find('input').attr('disabled', false);
        }
    });
    $.each($('.backup_daily').find('input'), function( key, value ) {
        if($(this).is(':checked')) {
            $(this).parents('form').find('.backup_daily_setting').show();
            $(this).parents('form').find('.backup_daily_setting').find('input').attr('disabled',false);
        }
    });
    $.each($('.backup_week').find('input'), function( key, value ) {
        if($(this).is(':checked')) {
            $(this).parents('form').find('.backup_weekly_setting').show();
            $(this).parents('form').find('.backup_weekly_setting').find('input').attr('disabled',false);
        }
    });
    $.each($('.backup_monthly').find('input'), function( key, value ) {
        if($(this).is(':checked')) {
            $(this).parents('form').find('.backup_monthly_setting').show();
            $(this).parents('form').find('.backup_monthly_setting').find('input').attr('disabled',false);
        }
    });

});
$('input:not(.ios-switch)').iCheck({
    checkboxClass: 'icheckbox_square-aero',
    radioClass: 'iradio_square-aero',
    increaseArea: '20%' // optional
});
$(document).on('ifToggled','.backup_daily',function (event) {
    event.preventDefault();
    if($(this).find('input').is(':checked')){
        $(this).parents('.checkbox').next('.backup_daily_setting').show();
        $(this).parents('.checkbox').next('.backup_daily_setting').find('input').attr('disabled',false);
    }else{
        $(this).parents('.checkbox').next('.backup_daily_setting').hide();
        $(this).parents('.checkbox').next('.backup_daily_setting').find('input[type="checkbox"]').iCheck('uncheck');
        $(this).parents('.checkbox').next('.backup_daily_setting').find('input').attr('disabled',true);
    }
});
$(document).on('ifToggled','.backup_week',function (event) {
    event.preventDefault();
    if($(this).find('input').is(':checked')){
        $(this).parents('.checkbox').next('.backup_weekly_setting').show();
        $(this).parents('.checkbox').next('.backup_weekly_setting').find('input').attr('disabled',false);
    }else{
        $(this).parents('.checkbox').next('.backup_weekly_setting').hide();
        $(this).parents('.checkbox').next('.backup_weekly_setting').find('input').attr('disabled',true);
    }
});
$(document).on('ifToggled','.backup_monthly',function (event) {
    event.preventDefault();
    if($(this).find('input').is(':checked')){
        $(this).parents('.checkbox').next('.backup_monthly_setting').show();
        $(this).parents('.checkbox').next('.backup_monthly_setting').find('input').attr('disabled',false);
    }else{
        $(this).parents('.checkbox').next('.backup_monthly_setting').hide();
        $(this).parents('.checkbox').next('.backup_monthly_setting').find('input').attr('disabled',true);
    }
});
$(document).on('ifToggled','.check_all_day',function (event) {
    event.preventDefault();
    if($(this).find('input').is(':checked')){
        $(this).parents('.backup_daily_setting').find('input[type="checkbox"]').iCheck('check');
    }else{
        $(this).parents('.backup_daily_setting').find('input[type="checkbox"]').iCheck('uncheck');
    }
});
$(document).on('ifToggled','.backup_type label',function (event) {
    event.preventDefault();
    if($(this).find('input').is(':checked') && $(this).find('input').val() == 2){
        $(this).parents('.cron-form').find('.ssh_config').show();
        $(this).parents('.cron-form').find('.ssh_config').find('input').attr('disabled',false);
    }else if($(this).find('input').prop('checked')==false && $(this).find('input').val() == 2){
        $(this).parents('.cron-form').find('.ssh_config').hide();
        $(this).parents('.cron-form').find('.ssh_config').find('input').attr('disabled',true);
    }
});

$(document).on('click','.delete_cronjob',function (event) {
    event.preventDefault();
    var buttonDelete = $(this);
    var id = $(this).parents('form.cron-form').find('input[name="id"]').val();
    var blok;
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about deleting cronjob?');
    $('.notifyjs-metro-base .d_yes').click(function(e) {
        e.preventDefault();
        $(this).trigger('notify-hide');
        if(id){
            $.ajax({
                url: "/cPanel/BackUps/deleteCronJob/"+id,
                type: "GET",
                dataType: "json",
                beforeSend: function () {
                    $('#loader').modal({backdrop: 'static', keyboard: false});
                    $('#loader').modal('show');
                },
                complete: function () {
                    $('#loader').modal('hide');
                },
                success: function (result) {
                    if (result.status) {
                        autohidenotify2('success', 'top right', 'Notification', result.msg, 8000);
                        if($('#content_blok').find('form.cron-form').length > 1){
                            buttonDelete.parents('form.cron-form').remove();
                        }else{
                            blok = removeBlok(buttonDelete.parents('form.cron-form'));
                            buttonDelete.parents('form.cron-form').find('.add_cronjob').html('Save');
                        }
                        $.each( $('#content_blok form.cron-form .title_blok'), function( key, value ){
                            $(this).html('CronTab #'+(key+1));
                        });

                    } else {
                        autohidenotify2('error', 'top right', 'Notification', result.msg, 8000);
                    }
                },
                error: function () {
                    autohidenotify2('error', 'top right', 'Notification', 'There is an error occurred when Delete Cronjob.', 8000);
                }
            });
        }else{
            if($('#content_blok').find('form.cron-form').length > 1){
                buttonDelete.parents('form.cron-form').remove();
            }else{
                blok = removeBlok(buttonDelete.parents('form.cron-form'));
            }
        }
        $.each( $('#content_blok form.cron-form .title_blok'), function( key, value ){
            $(this).html('CronTab #'+(key+1));
        });
    });
});
$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});


$(document).on('click','.add_block',function (event) {
    event.preventDefault();
    var blok = $(this).parents('.cron-form').clone(true);
    var count = $('#content_blok').find('form.cron-form').length + 1;
    blok = removeBlok(blok,count);
    blok.find('.add_cronjob').html('Save');
    blok.appendTo('#content_blok');

    $('input:not(.ios-switch)').iCheck({
        checkboxClass: 'icheckbox_square-aero',
        radioClass: 'iradio_square-aero',
        increaseArea: '20%' // optional
    });
    $('.backup_weekly_setting').find('div.iradio_square-aero').removeClass('disabled').change();
    $('.backup_daily_setting').find('div.icheckbox_square-aero').removeClass('disabled').change();
});

$(document).on('click','.add_cronjob',function (event) {
    event.preventDefault();
    if($(this).parents('form.cron-form').find('input[name="id"]').length){
        var id = $(this).parents('form.cron-form').find('input[name="id"]').val();
        var url = "/cPanel/BackUps/addCron/"+id
    }else{
        var url = "/cPanel/BackUps/addCron"
    }
    var formData = $(this).parents('.cron-form').serializeArray();
    var form = $(this).parents('form.cron-form');
    form.find('.error-message').hide();
    form.find('.error-input-ssh').remove();
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:function(){
            //before send
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        complete:function(){
            //complete
            $('#loader').modal('hide');
        },
        success: function (result) {
            if (result.status) {
                autohidenotify2('success', 'top right', 'Notification', result.msg, 8000);
                form.append('<input type="hidden" name="id" id="id" value="'+result.data.id+'">');
                form.find('.add_cronjob').html('Edit');
            } else {
                autohidenotify2('error', 'top right', 'Notification', result.msg, 8000);
                if (result.errors) {
                    if(result.errors.backup_schedu){
                        form.find('.error-schedule').show();
                        delete result.errors['backup_schedu'];
                    }
                    if(result.errors.backup_type){
                        form.find('.error-backup-type').show();
                        delete result.errors['backup_type'];
                    }
                    $.each( result.errors, function( key, value ) {
                        $.each( value, function( k, v ){
                            form.find('input[name="'+key+'"]').parent().append('<div class="error-message error-input-ssh" >'+v+'</div>');
                        });
                    });
                }
            }
        },
        error: function () {
            autohidenotify2('error', 'top right', 'Notification', 'There is an error occurred when add Cronjob.', 8000);
        }
    });

});
$(document).on('click','.add_retention',function (event) {
    event.preventDefault();
    var dataForm = $('form.retention-form').serializeArray();
    var form = $(this).parents('form.retention-form');
    form.find('.error-schedule-re').hide();
    form.find('.error-input-re').remove();
    $.ajax({
        url: "/cPanel/BackUps/addRetention",
        type: "POST",
        dataType: "json",
        data:dataForm,
        beforeSend:function(){
            //before send
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        complete:function(){
            //complete
            $('#loader').modal('hide');
        },
        success: function (result) {
            if (result.status) {
                autohidenotify2('success', 'top right', 'Notification', result.msg, 8000);
            } else {
                autohidenotify2('error', 'top right', 'Notification', result.msg, 8000);
                if (result.errors) {
                    if(result.errors.backup_schedu){
                        form.find('.error-schedule-re').show();
                        delete result.errors['backup_schedu'];
                    }
                    $.each( result.errors, function( key, value ) {
                        $.each( value, function( k, v ){
                            form.find('input[name="'+key+'"]').parent().append('<div class="error-message error-input-re" >'+v+'</div>');
                        });
                    });
                }

            }
        },
        error: function () {
            autohidenotify2('error', 'top right', 'Notification', 'There is an error occurred when add Retention.', 8000);
        }
    });
});

/**
 *
 * @param element
 * @returns {*}
 */
function removeBlok(element,count=0) {
    if(count){
        element.find('.title_blok').html('CronTab #'+count);
    }
    element.find('.widget-toggle').removeClass('closed');
    element.find('.widget-content').show();
    element.find('input[type="text"],input[type="number"],input[type="password"]').val('');
    element.find('input[type="checkbox"],input[type="radio"]').iCheck('uncheck');
    element.find('.backup_weekly_setting').hide();
    element.find('.error-message').hide();
    element.find('input[name="id"]').remove();
    element.find('.backup_weekly_setting').find('input').attr('disabled',true);
    element.find('.backup_daily_setting').hide();
    element.find('.backup_daily_setting').find('input').attr('disabled',true);
    element.find('.ssh_config').hide();
    element.find('.ssh_config').find('input').attr('disabled',true);
    return element;
}

$(document).on('click','.delete_retention',function (event) {
    event.preventDefault();
    var buttonDelete = $(this);
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about deleting cronjob?');
    $('.notifyjs-metro-base .d_yes').click(function(e) {
        e.preventDefault();
        $(this).trigger('notify-hide');
        $.ajax({
            url: "/cPanel/BackUps/deleteRetention/",
            type: "GET",
            dataType: "json",
            beforeSend: function () {
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete: function () {
                $('#loader').modal('hide');
            },
            success: function (result) {
                if (result.status) {
                    autohidenotify2('success', 'top right', 'Notification', result.msg, 8000);
                    buttonDelete.parents('form').find('input[type="checkbox"]').iCheck('uncheck');
                    buttonDelete.parents('form').find('input[type="text"]').val('');
                    buttonDelete.parents('form').find('.backup_daily_setting').hide();
                    buttonDelete.parents('form').find('.backup_daily_setting').find('input').attr('disabled',true);
                    buttonDelete.parents('form').find('.backup_weekly_setting').hide();
                    buttonDelete.parents('form').find('.backup_weekly_setting').find('input').attr('disabled',true);
                    buttonDelete.parents('form').find('.backup_monthly_setting').hide();
                    buttonDelete.parents('form').find('.backup_monthly_setting').find('input').attr('disabled',true);

                } else {
                    autohidenotify2('error', 'top right', 'Notification', result.msg, 8000);
                }
            },
            error: function () {
                autohidenotify2('error', 'top right', 'Notification', 'There is an error occurred when Delete Retention.', 8000);
            }
        });
    });
});