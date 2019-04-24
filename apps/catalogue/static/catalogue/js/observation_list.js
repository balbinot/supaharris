$(document).ready(function() {
    var table = $('#observations').DataTable({
        'serverSide': true,
        'processing': true,
        'language': {
            processing: '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i>'
        },
        'ajax': '/api/v1/catalogue/observation/?format=datatables',
        'columns': [
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
        ]
    });
});

