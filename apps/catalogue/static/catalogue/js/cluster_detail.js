function retrieve_cluster(pk) {
    $.ajax({ 
        type: 'GET', 
        url: '/api/v1/catalogue/globularcluster/' + pk + '?format=datatables', 
        dataType: 'json',
        success: function(cluster) {
            var r = new Array(), n = -1;
            r[++n] = '<tbody>';
            r[++n] = '<tr><th>Name</th><td>' + cluster.data.name + '</td></tr>';
            r[++n] = '<tr><th>Alias</th><td>' + cluster.data.altname+ '</td></tr>';
            r[++n] = '</tbody>';
            $('#cluster').html(r.join('')); 
        }
    });
};
