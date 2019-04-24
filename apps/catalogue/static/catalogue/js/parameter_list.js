$(document).ready(function() {
    var table = $('#parameters').DataTable({
        'serverSide': true,
        'pageLength': 50,
        'ajax': '/api/v1/catalogue/parameter/?format=datatables',
        'columns': [
            {
                'data': 'name',
                'render': function(data, type, row, meta){
                    console.log(data);
                    console.log(row);
                    if(type === 'display'){
                        data = '<a href="/catalogue/parameter/' + row.slug + '">' + row.name + '</a>';
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
