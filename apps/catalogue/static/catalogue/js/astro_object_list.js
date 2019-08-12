$(document).ready(function() {
    var table = $('#astro_objects').DataTable({
        'serverSide': true,
        'ajax': '/api/v1/catalogue/astro_object/?format=datatables',
        'columns': [
            {
                'data': 'name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/astro_object/' + row.slug+ '">' + row.name + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'altname'},
            {'data': 'slug', 'visible': false},  // to have slug available in row ...
        ]
    });
});
