$(document).ready(function() {
    var table = $('#clusters').DataTable({
        "serverSide": true,
        "ajax": "/api/v1/catalogue/globularcluster?format=datatables",
        "columns": [
            {"data": "name"},
            {
                "data": "slug",
                "render": function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + data + '">' + data + '</a>';
                    }
                    return data;
                }
            },
            {"data": "altname"},
        ]
    });
});
