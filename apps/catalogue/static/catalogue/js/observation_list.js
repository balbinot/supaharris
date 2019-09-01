$(document).ready(function() {
    var table = $('#observations').DataTable({
        'serverSide': false,
        'processing': true,
        'language': {
            processing: '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i>'
        },
        'ajax': '/api/v1/catalogue/observation/?format=datatables',
        'columns': [
            {
                'data': 'astro_object.name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/astro_object/' + row.astro_object.slug + '">' + row.astro_object.name + '</a>';
                    }
                    return data;
                }
            },
            {
                'data': 'parameter.name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/parameter/' + row.parameter.slug+ '">' + row.parameter.name + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'value'},
            {'data': 'sigma_up'},
            {'data': 'sigma_down'},
            {
                'data': 'reference.first_author',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/reference/' + row.reference.slug + '">' + row.reference.first_author + ' (' + row.reference.year + ')' + '</a>';
                    }
                    return data;
                }
            },
        ]
    });
});
