$(document).ready(function() {
    var table = $('#references').DataTable({
        "serverSide": true,
        "ajax": "/api/v1/catalogue/reference?format=datatables",
        "columns": [
            {"data": "bib_code"},
            {
                "data": "slug",
                "render": function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {"data": "ads_url"},
        ]
    });
});

