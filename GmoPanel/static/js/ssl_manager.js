$(document).on('click','.container-ssl',function (event) {
    event.preventDefault();
    if($('#icheck').is(':checked')){
        $('#formSll').find('textarea[name="ssl_crt"]').attr('disabled',true);
        $('#formSll').find('textarea[name="ssl_key"]').attr('disabled',true);
        $('#icheck').removeAttr("checked");
    }else{
        $('#formSll').find('textarea').removeAttr('disabled');
        $('#icheck').attr("checked","checked");
    }
})
$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});
$(document).on('click','.btn-let',function (event) {
    event.preventDefault();
    var id = $(this).data('id');
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Do you want to install SSL Let\'s encrypt?');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $(this).trigger('notify-hide');
        $.ajax({
            url: '/cPanel/SslManager/installLet/' + id,
            headers: {
                'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
            },
            type: "POST",
            dataType: "json",
            beforeSend: function () {
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete: function () {
                $('#loader').modal('hide');
            },
            success: function (result) {
                if (result.status == 1) {
                    autohidenotify2('success', 'top  right', 'Notification', result.msg, 8000);
                } else {
                    autohidenotify2('error', 'top  right', 'Notification', result.msg, 8000);
                }
            },
            error: function (xhr, textStatus, error) {
                autohidenotify2('error', 'top  right', 'Notification', 'An unknown error occured.', 8000);
            }
        });
    });
});

$(document).on('click','.btn-remove',function (event) {
    event.preventDefault();
    var id = $(this).data('id');
    $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Do you want to remove SSL?');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        $(this).trigger('notify-hide');
        $.ajax({
            url: '/cPanel/SslManager/removeSsl/' + id,
            headers: {
                'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
            },
            type: "POST",
            dataType: "json",
            beforeSend: function () {
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete: function () {
                $('#loader').modal('hide');
            },
            success: function (result) {
                if (result.status == 1) {
                    autohidenotify2('success', 'top  right', 'Notification', result.msg, 8000);
                } else {
                    autohidenotify2('error', 'top  right', 'Notification', result.msg, 8000);
                }
            },
            error: function (xhr, textStatus, error) {
                autohidenotify2('error', 'top  right', 'Notification', 'An unknown error occured.', 8000);
            }
        });
    });
});

$(document).on('click','.btn-manual',function (event) {
   event.preventDefault();
    $('#formSll').find('textarea').val('');
    $('#formSll').find('label.error').remove();
    $('#formSll').find('textarea,label').removeClass('error');
    $('#insallSll').removeAttr('data-id');
    $('#formSll').find('textarea').removeAttr('disabled');
    $('#domain_ssl').html('');
   var id = $(this).data('id');
   $.ajax({
       url: "/cPanel/SslManager/showSsl/"+id,
       headers : {
           'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
       },
       type: "POST",
       dataType: "json",
       beforeSend:function(){
           $('#loader').modal({backdrop: 'static', keyboard: false});
           $('#loader').modal('show');
       },
       complete:function(){
           $('#loader').modal('hide');
       },
       success: function (result) {
          if (result.status) {
              var count = 0;
              $('#domain_ssl').html(result.domain);
            if(result.crt){
                $('#formSll').find('textarea[name="ssl_crt"]').val(result.crt).attr('disabled',true);
                count ++;
            }
            if(result.key){
              $('#formSll').find('textarea[name="ssl_key"]').val(result.key).attr('disabled',true);
                count ++;
            }
            if(count == 0){
                $('#icheck').attr("checked","checked");
            }else{
                $('#icheck').removeAttr('checked');
            }
            $('#modal_instal_ssl').modal('show');
            $('#insallSll').attr('data-id',id);
          } else {

          }
       },
       error: function () {
           autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
       }
    })

});

$(document).on('click','#insallSll',function (event) {
    event.preventDefault();
    var id = $(this).attr('data-id');
    jQuery.validator.addMethod("valicrtssl", function(value, element) {
        if (/^(?:(?!-{3,}(?:BEGIN|END) CERTIFICATE)[\s\S])*(-{3,}BEGIN CERTIFICATE(?:(?!-{3,}END CERTIFICATE)[\s\S])*?-{3,}END CERTIFICATE-{3,})(?![\s\S]*?-{3,}BEGIN CERTIFICATE[\s\S]+?:-{3,}END CERTIFICATE[\s\S]*?$)/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Certificate chain is incorrect!');
    jQuery.validator.addMethod("valikeyssl", function(value, element) {
        if (/^(?:(?!-{3,}[\s\S]*PRIVATE KEY)[\s\S])*(-{3,}[\s\S]*PRIVATE KEY(?:(?!-{3,}[\s\S]*PRIVATE KEY)[\s\S])*?-{3,}[\s\S]*PRIVATE KEY-{3,})(?![\s\S]*?-{3,}[\s\S]*PRIVATE KEY[\s\S]+?-{3,}[\s\S]*PRIVATE KEY[\s\S]*?)$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Public key certificate is incorrect!');
    $('#formSll').validate({
        rules: {
            ssl_key:{
                required: true,
                valikeyssl : true
            },
            ssl_crt:{
                required: true,
                valicrtssl : true
            },
            icheck_ssl: "required"
        },
        messages:{
            ssl_key:{
                required: "Public key certificate is required."
            },
            ssl_crt:{
                required: "Certificate chain is required.",
            },
            icheck_ssl:{
                required: "You click edit !",
            },
        },
    });
    var validationResult = $('#formSll').valid();
    if(validationResult){
        var formData = $('#formSll').serializeArray();
        $.ajax({
            url: "/cPanel/SslManager/installManual/"+id,
            type: "POST",
            dataType: "json",
            data:formData,
            beforeSend:function(){
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            complete:function(){
                $('#loader').modal('hide');
            },
            success: function (result) {
               if (result.status) {
                   $('#modal_instal_ssl').modal('hide');
                   autohidenotify2('success','top  right','Notification',result.msg,8000);
               } else {
                   autohidenotify2('error','top  right','Notification',result.msg,8000);
               }
            },
            error: function () {
                autohidenotify2('error','top  right','Notification','An unknown error occured.',8000);
            }
         })
    }
});

$(document).on('click','.check-ssl-btn',function (event) {
    event.preventDefault();
    let id = $(this).data('id');
    let thisBtn = $(this);
    $.ajax({
        url: '/cPanel/SslManager/checkSsl/',
        headers: {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: "POST",
        data: {
            id: id
        },
        dataType: "json",
        beforeSend: function () {
            thisBtn.button('loading');
        },
        complete: function () {
            thisBtn.button('reset');
        },
        success: function (result) {
            if (result.status) {
                if(result.install){
                    $('#subject').html(result.msg.subject);
                    $('#issuer').html(result.msg.issuer);
                    $('#from').html(result.msg.from);
                    $('#to').html(result.msg.to);
                    $('#duration').html(result.msg.duration);
                    $('#modal_status_ssl').modal('show');
                }else{
                    thisBtn.parent().html(result.msg);
                }
            } else {
                autohidenotify2('error', 'top  right', 'Notification', result.msg, 8000);
            }
        },
        error: function (xhr, textStatus, error) {
            autohidenotify2('error', 'top  right', 'Notification', 'An unknown error occured.', 8000);
        }
    });
});