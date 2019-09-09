$(document).ready(function() {
    var table = $('#astro_objects').DataTable({
        'serverSide': true,
        'processing': true,
        'lengthMenu': [[10, 25, 50, 100, 500, 1000, 5000], [10, 25, 50, 100, 500, 1000, 5000]],
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
            {'data': 'classifications', 'name': 'classifications.name'},
            {'data': 'frontend_url', 'visible': false, 'searchable': false},
        ]
    });
});
