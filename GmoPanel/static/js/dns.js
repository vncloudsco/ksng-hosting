$(document).ready(function () {
    $(document).ready(function () {
        var zone = $('#form-dns').find('input[name="zone"]').val();
        $('#listDns').DataTable({
            paging: false,
            lengthChange: false,
            searching: true,
            ordering: false,
            info: true,
            autoWidth: false,
            processing: true,
            serverSide: true,
            ajax: {
                type: "POST",
                headers : {
                    'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
                },
                url: "/cPanel/Dns/renderTable/"+zone
            },
            columns: [
                {data: "DnsRecord.index"},
                {data: "DnsRecord.host"},
                {data: "DnsRecord.ttl"},
                {data: "DnsRecord.class"},
                {data: "DnsRecord.type"},
                {data: "DnsRecord.value"},
                {data: "DnsRecord.action"},

            ],
            fnDrawCallback: function () {
            },
        });
    });
    function filterColumn(i, value) {
        $('#listDns').DataTable().column(i).search(value).draw();
    }
    $(document).on("click", '#searchDns', function (event) {
        event.preventDefault();
        var datastring = $("#formSearch").serialize();
        filterColumn(5, datastring);
    });
});
$(document).on('change','#type-dns',function () {
    var arr = ['A','AAAA','MX','TXT','SRV','CNAME','NS'];
    $("#form-dns").find('.error').prev().remove();
    $("#form-dns").find('.error').remove();
    var value = $(this).val().toString();
    if(jQuery.inArray( value, arr ) || value == 'A'){
        addHtmlSelect(value);
    }
});

$(document).on('click','.add-dns',function(){
    var html = '<input type="text" placeholder="IPV4 address" name="value" />';
    $('#addDns').find('input,select,textarea').val('');
    $('#addDns').find('.error').prev().remove();
    $('#addDns').find('.error').remove();
    $('#type-dns').val('A');
    $('#data-form').html(html);
    $('#alert-msg').hide();
    $('#saveDns').html('Add');
});

$(document).on('click','#saveDns',function (event) {
    event.preventDefault();
    $("#form-dns").find('.error').prev().remove();
    $("#form-dns").find('.error').remove();
    $('#alert-msg').hide();
    var type = $("#form-dns").find('select[name="type"]').val();
    var datastring = $("#form-dns").serializeArray();
    $.ajax({
        url: "/cPanel/Dns/changeDns/"+type,
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: "POST",
        dataType: "json",
        data: datastring,
        beforeSend: function() {
            $('#saveDns').hide();
            $('#icon-load').show();
        },
        success: function (result) {
            if (result.status) {
                notify('success','top right',result.msg);
                $('#modal-dns').modal('hide');
                $('#listDns').DataTable().draw();
            } else {
                if(result.error){
                    $.each(result.error, function (index, value) {
                        var nameError = "";
                        var labelError = "";
                        $.each(value, function (i, v) {
                            nameError = v;
                            labelError = '<br/><span class="error">' + v + '</span>';
                        });
                        if(!$("#form-dns").find('input[name="' + index + '"]').is(":hidden")){
                            $("#form-dns").find('input[name="' + index + '"]').after(labelError);
                        }
                        $("#form-dns").find('textarea[name="' + index + '"]').after(labelError);
                        if (index == 'type') {
                            $("#form-dns").find('select[name="' + index + '"]').after(labelError);
                        }
                        if(index=='zone'){
                            autohidenotify('error','top right','Notifications',nameError);
                        }
                    });
                }else{
                    autohidenotify('error','top right','Notifications',result.msg);
                }

            }
        },
        error: function () {
            $('#saveDns').show();
            $('#icon-load').hide();
            autohidenotify('error','top right','Notifications','Can not connect!');
        },
        complete: function() {
            $('#saveDns').show();
            $('#icon-load').hide();
        },
    })

});

$(document).on('click','.dns-edit',function (event) {
    event.preventDefault();
    $('#addDns').find('.error').prev().remove();
    $('#addDns').find('.error').remove();
    var id = $(this).data('id');
    var zone = $('#form-dns').find('input[name="zone"]').val();
    $('#saveDns').html('Change');
    $.ajax({
        url: "/cPanel/Dns/findDnsById/"+id+"/"+zone,
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: "GET",
        dataType: "json",
        data: {
        },
        success: function (result) {
            if (result.status) {
                addHtmlSelect(result.data.type);
                $.each(result.data, function (index, value) {
                    $('#form-dns').find('input[name="'+index+'"]').val(value);
                    $('#form-dns').find('select[name="'+index+'"]').val(value);
                    $('#form-dns').find('textarea[name="'+index+'"]').val(value);
                });
                $('#modal-dns').modal('show');
                $('#alert-msg').hide();
            } else {
                autohidenotify('error','top right','Notifications','Bạn hãy thử lại sau!');
            }
        },
        error: function () {
            $('#alert-msg').show();
            $('#alert-msg').html('Bạn hãy thử lại sau!');
        },
    });
});

$(document).on('click','.dns-delete',function (event) {
    event.preventDefault();
    var id = $(this).data('id');
    $('#deleteDns').attr('data-id',id);
});

$(document).on('click','#deleteDns',function (event) {
    event.preventDefault();
    $('#md-3d-sign-confirm').modal('hide');
    var idDns = $(this).attr('data-id');
    var zone = $('#form-dns').find('input[name="zone"]').val();
    var account_id = $('#form-dns').find('input[name="account_id"]').val();
    $.ajax({
        url: "/cPanel/Dns/deleteDns/",
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: "POST",
        dataType: "json",
        data: {
            id:idDns,
            zone:zone,
            account_id:account_id
        },
        beforeSend: function() {
            $('#loader').modal({backdrop: 'static', keyboard: false});
            $('#loader').modal('show');
        },
        success: function (result) {
            $('#loader').modal('hide');
            if (result.status) {
                notify('success','top right',result.msg);
                $('#listDns').DataTable().draw();
            } else {
                autohidenotify('error','top right','Notifications',result.msg);
            }
        },
        error: function () {
            $('#loader').modal('hide');
            autohidenotify('error','top right','Notifications','Bạn hãy thử lại sau !');
        },
    });
});
/**
 * add html
 * @param value
 */
function addHtmlSelect(value) {
    var html = '<input type="text" placeholder="IPV4 address" name="value" />';
    switch(value) {
        case 'A':
            html = '<input type="text" placeholder="IPV4 address" name="value" />';
            $('#data-form').html(html);
            break;
        case 'AAAA':
            html = '<input type="text" placeholder="IPV6 address" name="value" />';
            $('#data-form').html(html);
            break;
        case 'CNAME':
            html = '<input type="text" placeholder="Fully qualified domain name" name="value" />';
            $('#data-form').html(html);
            break;
        case 'MX':
            html = '<div class="form-group" style="width: 100%;float: right;text-align: right"><label >Priority :</label>';
            html += '<input class="input-dns" type="text" placeholder="integer" name="priority" /></div>';
            html += '<br/>';
            html += '<div class="form-group" style="width: 100%;float: right;text-align: right"><label>Destination :</label>';
            html += '<input class="input-dns" type="text" placeholder="Fully qualified domain name" name="value" /></div>';
            $('#data-form').html(html);
            break;
        case 'SRV':
            html = '<div class="form-group" style="width: 100%;float: right;text-align: right"><label >Priority :</label>';
            html += '<input class="input-dns" type="text" placeholder="integer" name="priority" /></div>';
            html += '<br/>';
            html += '<div class="form-group" style="width: 100%;float: right;text-align: right"><label >Weight :</label>';
            html += '<input class="input-dns" type="text" placeholder="Integer" name="weight"/></div>';
            html += '<div class="form-group" style="width: 100%;float: right;text-align: right"><label >Port :</label>';
            html += '<input class="input-dns" type="text" placeholder="port number" name="port" /></div>';
            html += '<br/>';
            html += '<div class="form-group" style="width: 100%;float: right;text-align: right"><label >Target :</label>';
            html += '<input class="input-dns" type="text" placeholder="valid zone name" name="target" /></div>';
            $('#data-form').html(html);
            break;
        case 'TXT':
            html = '<textarea placeholder="Text" name="value" rows="5" cols="30" />';
            $('#data-form').html(html);
            $('#data-form').css('width','100%');
            break;
        case 'NS':
            html = '<input type="text" placeholder="Fully qualified domain name" name="value" />';
            $('#data-form').html(html);
            break;
        default:
            alert('error');
    }
}