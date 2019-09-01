function retrieve_astro_object_observations(pk) {
    var table = $('#observations' + pk).DataTable({
        'serverside': false,
        'pageLength': 50,
        'ajax': '/api/v1/catalogue/observation/?astro_object=' + pk + '&format=datatables',
        'columns': [
            {
                'data': 'parameter.name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + row.frontend_url
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
