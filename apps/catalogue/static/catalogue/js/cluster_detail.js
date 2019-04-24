function retrieve_cluster_observations(pk) {
    var table = $('#observations' + pk).DataTable({
        'serverSide': true,
        'ajax': '/api/v1/catalogue/observation/?cluster=' + pk + '&format=datatables',
        'columns': [
            {
                'data': 'parameter.name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/parameter/' + row.parameter.slug
                            + '" data-toggle="tooltip" data-placement="right" title="'
                            + row.parameter.description + '">' + row.parameter.name + '</a>';
                    }
                    return data;
                }
            },
            { 'data': 'value' },
            { 'data': 'sigma_up' },
            { 'data': 'sigma_down' },
            {
                'data': 'reference',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/reference/' + row.reference.slug
                            + '">' + row.reference.first_author + ' (' + row.reference.year + ')</a>';
                    }
                    return data;
                }
            },
        ]
    });
};
