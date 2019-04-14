$(document).ready(function() {
    var table = $('#references').DataTable({
        "serverSide": true,
        "ajax": "/api/v1/catalogue/reference?format=datatables",
        "columns": [
            {"data": "bib_code"},
            {"data": "ads_url"},
        ]
    });
});

