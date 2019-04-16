$(document).ready(function() {
    var table = $('#clusters').DataTable({
        'serverSide': true,
        'ajax': '/api/v1/catalogue/globularcluster/?format=datatables',
        'columns': [
            {
                'data': { slug: 'slug', name: 'name' },
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + row.slug+ '">' + row.name + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'altname'},
        ]
    });
});
