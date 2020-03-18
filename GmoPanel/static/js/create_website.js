function makeid(count) {
        var text = "";
        var possible = "abcdefghijklmnopqrstuvwxyz0123456789";

        for (var i = 0; i < count; i++)
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
    }
$(document).ready(function() {

});

$(document).on('click','#submit-btn',function(event) {
    event.preventDefault();
    $.validator.addMethod("userpassword", function(value, element) {
        if (/^[a-zA-Z0-9.!#%+_-]+$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Password must be in a->z, A->Z, 0->9 or those .!#%+_-');

    jQuery.validator.addMethod("username", function(value, element) {
        if (/^[a-zA-Z0-9_]+$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Username must be in a->z, A->Z, 0->9 or those _');
    jQuery.validator.addMethod("username_default", function(value, element) {
        if (value != "root") {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Database username must be in a->z, A->Z, 0->9 or those ._- and different from "root"');

    jQuery.validator.addMethod("dbname", function(value, element) {
        if (/^[a-zA-Z0-9_]+$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Database name must be in a->z, A->Z, 0->9 or those _');

    jQuery.validator.addMethod("dbpassword", function(value, element) {
        if (/^[a-zA-Z0-9]+$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Database password must be in a->z, A->Z or 0->9');

    jQuery.validator.addMethod("domain", function(value, element) {
        if (/^(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}$/.test(value)) {
            return true;   // PASS validation when REGEX matches
        } else {
            return false;  // FAIL validation
        };
    }, 'Domain is incorrect. Example: mydomain.com');

    $('#saveForm').validate({
        rules: {
            db_password:{
                minlength: 8,
                dbpassword: true,
            },
            db_username:{
                minlength: 3,
                maxlength: 16,
                username: true,
                username_default: true
            },
            db_name:{
                minlength: 3,
                maxlength: 64,
                dbname: true,
            },
            email: {
                email: true,
            },
            domain_name: {
                domain:true,
            }
        },
        messages:{
            domain_name:{
                required: "This field is required."
            },
            email:{
                required: "This field is required.",
                email: "Email is incorrect."
            },
            db_name:{
                required: "This field is required.",
                maxlength: "Maximum length is 64 characters.",
                minlength: "Minimum length is 3 characters.",
            },
            db_username:{
                required: "This field is required.",
                maxlength: "Maximum length is 16 characters.",
                minlength: "Minimum length is 3 characters.",
            },
            db_password:{
                required: "This field is required.",
                minlength: "Minimum length is 8 characters."
            }
        },
    });

    var validationResult = $('#saveForm').valid();
    if(validationResult){
        var dataForm = $('#saveForm').serializeArray();
        var domainname = $('#domain_name').val();
        var url = "/websites/createProvision/";
        var method = 'POST';
        $.ajax({
            url: url,
            type: method,
            data: dataForm,
            dataType: 'json',
            beforeSend: function(){
                notify2('cool','top right','This may take a few minutes.','#submit-btn');
                $('#submit-btn').button('loading');
            },
            complete: function(){
                $('#submit-btn').button('reset');
            },
            success: function(result) {
                if(result.status){
                    autohidenotify2('success','top right','Notification','Creating website is completed successfully. Please access <a target="_blank" href="http://'+domainname+'">http://'+domainname+'</a> to check it out.',8000);
                    $('#reset_form').click();
                }else{
                    autohidenotify2('error','top right','Notification',result.msg,8000);
                    if(result.errors){
                        $.each(result.errors, function (index, value) {
                            var labelError = "";
                            $.each(value, function (i, v) {
                                labelError = '<label id="'+index+'-error" class="error" for="'+index+'">'+v+'</label>';
                            });
                            $("#saveForm").find('input[name="' + index + '"]').after(labelError);
                        });
                    }
                }
            },
            error: function() {
                notify('error','top right','There is an error occurred when creating website.');
            }
        });
    }
});

$(document).on('click','.cms_tab',function (event) {
    event.preventDefault();
    $('#saveForm').find('input[name="app_id"]').val($(this).attr('myid')).change();
})

$(document).on('blur','#domain_name',function(event) {
    var domain_name = $(this).val();
    if(domain_name != ''){
        var custom_domain = domain_name.substring(0,5) + makeid(3) + '_';
        custom_domain = custom_domain.replace(/\.|\-/gi,'_');
        $('#db_name').val(custom_domain+'db');
        $('#db_username').val(custom_domain+'user');
    }
});