$(document).ready(function() {
    var table = $('#astro_objects').DataTable({
        'serverSide': false,
        'processing': true,
        'ajax': '/api/v1/catalogue/astro_object/?format=datatables',
        'columns': [
            {
                'data': 'name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + row.frontend_url + '">' + row.name + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'altname'},
            {'data': 'classifications', 'searchable': false},
            {'data': 'frontend_url', 'visible': false, 'searchable': false},
        ]
    });
});
