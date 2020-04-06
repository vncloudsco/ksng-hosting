var url = $(location).attr('href').split("/").splice(3, 1).join("/");
var action = $(location).attr('href').split("/").splice(4, 1).join("/");
if(url == ''){
    $('.my-menu').children().eq(0).children().eq(0).addClass('active');
}
switch(url){
    case 'websites':
        if (action == 'listMysql'){
            $('.my-menu').children().eq(5).children().eq(0).addClass('active');
        }else if(action == 'emailServer'){
            $('.my-menu').children().eq(6).children().eq(0).addClass('active');
        }else{
            $('.my-menu').children().eq(1).children().eq(0).addClass('active');
        }
        break;
    case 'backups':
        $('.my-menu').children().eq(2).children().eq(0).addClass('active');
        break;
    case 'Upload':
        $('.my-menu').children().eq(4).children().eq(0).addClass('active');
        break;
    case 'MysqlManager':
        $('.my-menu').children().eq(5).children().eq(0).addClass('active');
        break;
    case 'SslInstaller':
        $('.my-menu').children().eq(10).children().eq(0).addClass('active');
        break;
    case 'EmailServer':
        $('.my-menu').children().eq(6).children().eq(0).addClass('active');
        break;
    case 'Accounts':
        $('.my-menu').children().eq(7).children().eq(0).addClass('active');
        break;
    case 'settings':
        $('.my-menu').children().eq(7).children().eq(0).addClass('active');
        break;
    case 'waf':
        $('.my-menu').children().eq(8).children().eq(0).addClass('active');
        break;
    case 'securitys':
        $('.my-menu').children().eq(8).children().eq(0).addClass('active');
        break;
    default:
        $('.my-menu').children().eq(0).children().eq(0).addClass('active');
}

$('#goto').click(function(event) {
    var url = "/websites/fileManager";
    var method = 'POST';
    $.ajax({
        url: url,
        headers : {
            'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
        },
        type: method,
        data: {

        },
        dataType: "json",
        beforeSend: function(){
            
        },
        success: function(result) {
            if(result.status == 1){
                var url = result.url;
                window.open(url);
            }else{
                var error = result.msg;
                alert(error);
            }
        },
        async: false,
        error: function(xhr, textStatus, error) {
            
        }
    });
});

$('#wb-button').click(function(event) {
    $('#wb_result').html('<div style="width:100% !important;height:100%" class="lds-facebook"><div style="left:42% !important;"></div><div></div><div style="left:58% !important;"></div></div>');
    setTimeout(function(){
        var url = "/websites/modal/";
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
                $('#wb_result').hide().html(result).fadeIn('slow');
            },
            async: false,
            error: function(xhr, textStatus, error) {
                
            }
        });
    }, 1000);
});

$('#wordpress-upload').click(function(event) {
    $('#wp_u_result').html('<div style="width:100% !important;height:100%" class="lds-facebook"><div style="left:42% !important;"></div><div></div><div style="left:58% !important;"></div></div>');
    setTimeout(function(){
        var url = "/uploads/modal/wordpress";
        var method = 'GET';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            beforeSend: function(){
                
            },
            success: function(result) {
                $('#wp_u_result').hide().html(result).fadeIn('slow');
            },
            async: false,
            error: function(xhr, textStatus, error) {
                
            }
        });
    }, 1000);
});

$('#database-upload').click(function(event) {
    $('#database_u_result').html('<div style="width:100% !important;height:100%" class="lds-facebook"><div style="left:42% !important;"></div><div></div><div style="left:58% !important;"></div></div>');
    setTimeout(function(){
        var url = "/uploads/modal/database";
        var method = 'GET';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            beforeSend: function(){
                
            },
            success: function(result) {
                $('#database_u_result').hide().html(result).fadeIn('slow');
            },
            async: false,
            error: function(xhr, textStatus, error) {
                
            }
        });
    }, 1000);
});

$('#source-upload').click(function(event) {
    $('#source_u_result').html('<div style="width:100% !important;height:100%" class="lds-facebook"><div style="left:42% !important;"></div><div></div><div style="left:58% !important;"></div></div>');
    setTimeout(function(){
        var url = "/uploads/modal/source";
        var method = 'GET';
        $.ajax({
            url: url,
            headers : {
                'X-CSRFToken': getCookie('csrftoken')
            },
            type: method,
            beforeSend: function(){
                
            },
            success: function(result) {
                $('#source_u_result').hide().html(result).fadeIn('slow');
            },
            async: false,
            error: function(xhr, textStatus, error) {
                
            }
        });
    }, 1000);
});

