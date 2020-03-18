$(document).on('click','.backup_pro',function (event) {
    event.preventDefault();
    $('#modal_backup_pro').modal('show');
    $('#type_backup').val(0).change();
    $('#ssh_config').find('input').val('');
    $('#pro_id').val($(this).attr('data-id'));
    $('#path_local').show().change();
    domain = $(this).parents('tr').find('td:nth-child(2)').html();
    $('#domain_backup').html(domain).change();
});

$(document).on('change','#type_backup',function (event) {
    event.preventDefault();
    if($(this).val() == 1){
        $('#ssh_config').show();
        $('#path_local').hide().change();
        $('#driver_config').hide().change();
        $('#ssh_config').find('input').val('');
        $('#ssh_config').find('input').attr('disabled',false);
        $('#driver_config').find('input').attr('disabled',true);

    }else if($(this).val() == 2){
        $('#ssh_config').hide();
        $('#path_local').hide().change();
        $('#driver_config').show().change();
        $('#driver_config').find('input').val('/backup/');
        $('#driver_config').find('input').attr('disabled',false);
    }
    else{
        $('#ssh_config').hide();
        $('#path_local').show().change();
        $('#driver_config').hide().change();
        $('#ssh_config').find('input').attr('disabled',true);
        $('#driver_config').find('input').attr('disabled',true);
    }
});

$(document).on('click','#backupPro',function (event) {
    event.preventDefault();
    var dataForm = $('#formBackup').serializeArray();
    var url = "/backups/action/" + $('#pro_id').val();
    $("#formBackup").find('span.error').remove();
    var method = 'POST';
    $.ajax({
        url: url,
        headers : {
            'X-CSRFToken': getCookie('csrftoken')
        },
        type: method,
        data: dataForm,
        dataType: 'json',
        beforeSend: function () {
            notify2('cool', 'top right', 'This may take a few minutes.', '#backupPro');
            $('#backupPro').button('loading');
        },
        complete: function () {
            $('#backupPro').button('reset');
        },
        success: function (result) {
            if (result.status) {
                autohidenotify2('success', 'top right', 'Notification', result.msg, 8000);
                $('#modal_backup_pro').modal('hide');
            } else {
                autohidenotify2('error', 'top right', 'Notification', result.msg, 8000);
                if(result.errors){
                    $.each(result.errors, function (index, value) {
                        var labelError = "";
                        labelError = '<span id="'+index+'-error" class="error" for="'+index+'">'+value[0]+'</span>';
                        console.log(labelError)
                        $("#formBackup").find('input[name="' + index + '"]').after(labelError);
                    });
                }
            }
        },
        error: function () {
            notify('error', 'top right', 'There is an error occurred when backup website.');
        }
    });
});

