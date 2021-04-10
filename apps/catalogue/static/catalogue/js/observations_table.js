function retrieve_observation_table_columns() {
    var columns = [];
    $.ajax({
        type: 'GET',
        url: '/api/v1/catalogue/observation_table/?format=json',
        dataType: 'json',
        async: false,
        success: function(data) {
            columns = data.results[0];
        }
    });
    return columns;
}

function set_observation_table_header(columns) {
    var r = new Array(), n = -1;
    r[++n] = '<tr>';
    Object.entries(columns).forEach(([key, value]) => {
        r[++n] = '<th>' + key + '</th>';
    });
    r[++n] = '</tr>';
    $('#observationsTableHead').html(r.join(''));
    $('#observationsTableFoot').html(r.join(''));
}


function set_observation_table(columns) {
    var cols = new Array(), n = -1;
    Object.entries(columns).forEach(([key, value]) => {
        cols[++n] = {'data': key};
    });
    var table = $('#observationsTable').DataTable({
        'serverSide': false,
        'processing': true,
        'lengthMenu': [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        'ajax': '/api/v1/catalogue/observation_table/?format=datatables',
        'order': [[ 1, 'asc' ]],
        'columns': cols
    });
}
