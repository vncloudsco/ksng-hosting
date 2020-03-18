$(document).ready(function () {
    var elem = document.querySelector('.js-switch');
    var init = new Switchery(elem);
});

$(document).on('click','.change_security',function (event) {
    event.preventDefault();
    $.ajax({
        url: '/cPanel/Securitys/getSecurityCode',
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: 'POST',
        data: null,
        dataType: 'json',
        beforeSend: function(){
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        complete: function(){
            $('#loader').modal('hide');
        },
        success: function(result) {
            if(result.status){
                $('#security-code').val(result.securityCode);
                $('#img_security').attr('src',result.qrCodeUrl);
            }
        },
        error: function(xhr, textStatus, error) {
            notify('error','top right','There is an error occurred when creating website.');
        }
    });
});