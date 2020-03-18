$(document).ready(function () {
    $('#listDomain').DataTable({
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
            url: "/cPanel/DomainDns/renderTable/"
        },
        columns: [
            {data: "Provision.index"},
            {data: "Provision.domain_name"},
            {data: "Provision.created"},
            {data: "Provision.status"},
            {data: "Provision.dns"},

        ],
    });
});

function filterColumn(i, value) {
    $('#listDomain').DataTable().column(i).search(value).draw();
}

$(document).on("click", '#domainSearch', function (event) {
    event.preventDefault();
    var datastring = $("#formSearch").serialize();
    filterColumn(4, datastring);
});

$(document).on('click', '.delete-domain', function (event) {
    event.preventDefault();
    var id = $(this).data('id');
    $('#deleteDomain').attr('data-id', id);
});

$(document).on('click', '#deleteDomain', function (event) {
    event.preventDefault();
    var id = $(this).data('id');
    if (id) {
        $('#md-delete-domain-confirm').modal('hide');
        $.ajax({
            url: "/cPanel/DomainDns/deleteDomain/" + id,
            headers : {
                'X-CSRF-Token': $('#form-get-token').find('input[name="_csrfToken"]').val()
            },
            type: "GET",
            dataType: "json",
            data: {},
            beforeSend: function () {
                $('#loader').modal({backdrop: 'static', keyboard: false});
                $('#loader').modal('show');
            },
            success: function (result) {
                $('#loader').modal('hide');
                if (result.status) {
                    notify('success', 'top right', result.msg);
                    $('#listDomain').DataTable().draw();
                } else {
                    autohidenotify('error', 'top right', 'Notifications', result.msg);
                }
            },
            error: function () {
                $('#loader').modal('hide');
                autohidenotify('error', 'top right', 'Notifications', 'Bạn hãy thử lại sau !');
            },
        });
    }
});