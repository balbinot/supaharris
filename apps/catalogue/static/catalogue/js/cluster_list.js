$(document).ready(function() {
    var table = $('#clusters').DataTable({
        "serverSide": true,
        "ajax": "/api/v1/catalogue/globularcluster?format=datatables",
        "columns": [
            {"data": "name"},
            {"data": "slug"},
            {"data": "altname"},
        ]
    });
});
