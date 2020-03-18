$(document).ready(function(){
    loadDomain();
    var loading_zone = $('#domain_list').html();
});
function loadDomain(){
    var url = "/websites/listDomain/";
    var method = 'POST';
    $.ajax({
        url: url,
        headers : {
            'X-CSRFToken': getCookie('csrftoken')
        },
        type: method,
        data: {
        },
        beforeSend: function(){
        },
        success: function(result) {
            $('#domain_list').hide().html(result).fadeIn('slow');
        },
        error: function(xhr, textStatus, error) {

        }
    });
}
$(document).on('click', '.notifyjs-metro-base .d_no', function() {
    $(this).trigger('notify-hide');
});
/**
 * delete domain ajax
 */
$(document).on('click','.delete_domain',function(event){
   event.preventDefault();
   $('.notifyjs-wrapper').remove();
    nconfirm2('Notification','Are you sure about deleting this website?');
    var id = $(this).data('id');
    $('.notifyjs-metro-base .d_yes').click(function(event) {
        event.preventDefault();
        $(this).trigger('notify-hide');
        var url = "/websites/deleteProvision/";
        var method = 'POST';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            data: {
                id: id,
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
                loadDomain();
                if(result.status == 1){
                    autohidenotify2('success','top right','Notification','Deleting website is completed successfully!',8000);
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                }
            },
            error: function() {
                notify('error','top right','There is an error occurred when deleting website.');
            }
        });
    });
});
