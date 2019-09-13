$(document).ready(function() {
    var table = $('#parameters').DataTable({
        'serverSide': false,
        'processing': true,
        'pageLength': 50,
        'lengthMenu': [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        'ajax': '/api/v1/catalogue/parameter/?format=datatables',
        'columns': [
            {
                'data': 'name',
                'render': function(data, type, row, meta){
                    console.log(data);
                    console.log(row);
                    if(type === 'display'){
                        data = '<a href="' + row.frontend_url + '">' + row.name + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'description'},
            {'data': 'unit'},
            {'data': 'scale'},
            {'data': 'slug', 'visible': false},  // to have slug available in row ...
        ]
    });
});
