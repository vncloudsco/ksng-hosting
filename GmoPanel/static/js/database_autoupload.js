$(document).ready(function() {
    $('#dropzone').click(function(){
        $('#fileupload').click();
    });

    $('#execute-btn').click(function(){
        let upload_domain = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
        var url = "/uploads/executeDatabase/"+upload_domain;
        var method = 'GET';
        if(upload_domain != ''){
            $.ajax({
                url: url,
                headers : {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                type: method,
                dataType: "json",
                beforeSend: function(){
                    $('#execute-btn').button('loading');            
                },
                success: function(data) {
                    if(data.status == 1){
                        $('#container-main').hide().html('<div class="alert alert-info"><strong>Success!</strong> Your database is uploaded successfully to your website. Click <a target=_blank href=http://'+upload_domain+'>HERE</a> to checkout or <a href="/cPanel"> go back homepage.</a></div>').fadeIn( "slow");
                    }else{
                        $('#container-main').hide().html('<div class="alert alert-danger"><strong>Error!</strong> '+data.msg+'</div>').fadeIn("1000");    
                    }
                    $('#execute-btn').button('reset');
                },
                error: function(xhr, textStatus, error) {
                    alert('Executed..!');
                    $('#execute-btn').button('reset');
                }
            });
        }else{
            alert('The domain can not be found.');
        }
    });
});

$(function () {
    $(document).bind('dragover', function (e) {
        var dropZone = $('#dropzone'),
            timeout = window.dropZoneTimeout;
        if (timeout) {
            clearTimeout(timeout);
        } else {
            dropZone.addClass('in');
        }
        var hoveredDropZone = $(e.target).closest(dropZone);
        dropZone.toggleClass('hover', hoveredDropZone.length);
        window.dropZoneTimeout = setTimeout(function () {
            window.dropZoneTimeout = null;
            dropZone.removeClass('in hover');
        }, 100);
    });
    
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });
    
    let _csrfToken = $('#form-get-token').find('input[name="_csrfToken"]').val();
    let domain_name = ($('#pro_id').val() != '') ? $('#pro_id').val() : '';
    $('#fileupload').fileupload({
        // dataType: 'json',
        add: function (e, data) {
            $('#loading_position').append('<div class="alert alert-warning" id="'+ data.files[0].size +'"><i class="fa fa-refresh fa-spin"></i> Uploading <strong>'+ data.files[0].name +'</strong></div>');
            $('.progress-bar').css(
                'width','0%'
            );
            $('.progress-bar').text('0%');

            $('#progress-container').show();
            // $('#dropzone').remove();
            data.submit();
        },
        done: function (e, data) {
            $('#' + data.files[0].size).removeClass('alert alert-warning');
            $('#' + data.files[0].size).addClass('alert alert-info');
            $('#' + data.files[0].size).html('Finished upload <strong>'+ data.files[0].name +'</strong>');
        },
        maxChunkSize: 10000000 , //10MB
        dropZone: $('#dropzone'),
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('.progress-bar').css(
                'width',
                progress + '%'
            );
            $('.progress-bar').text(progress + '%');
        },
        fail: function (e, data) {
            alert('upload fail');
        }
    }).bind('fileuploadstop', function (e) {
        $('.progress-bar').removeClass('progress-bar-striped').addClass('progress-bar-primary');
        $('#container-exe').fadeIn("1000");
    });
});