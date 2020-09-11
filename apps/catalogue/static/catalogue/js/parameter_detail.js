function retrieve_parameter(pk) {
    $.ajax({
        type: 'GET',
        url: '/api/v1/catalogue/parameter/' +pk + '?format=datatables',
        dataType: 'json',
        success: function(parameter) {
            var r = new Array(), n = -1;
            r[++n] = '<tbody>';
            r[++n] = '<tr><th>Parameter</th><td>' + parameter.data.name + '</td></tr>';
            r[++n] = '<tr><th>Description</th><td>' + parameter.data.description + '</td></tr>';
            r[++n] = '<tr><th>unit</th><td>' + parameter.data.unit + '</td></tr>';
            r[++n] = '<tr><th>scale</th><td>' + parameter.data.scale + '</td></tr>';
            r[++n] = '</tbody>';
            $('#parameter').html(r.join(''));
        }
    });
};
