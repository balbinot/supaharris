function retrieve_reference(pk) {
    $.ajax({ 
        type: 'GET', 
        url: '/api/v1/catalogue/reference/' + pk + '?format=datatables', 
        dataType: 'json',
        success: function(reference) {
            if (reference.data.ads_url.toLowerCase().includes('arxiv.org')) {
                var ads_or_arxiv = 'arXiv';
            } else if (reference.data.ads_url.toLowerCase().includes('ads')) {
                var ads_or_arxiv = 'ADS';
            } else {
                var ads_or_arxiv = null;
            }
            var r = new Array(), n = -1;
            r[++n] = '<tbody>';
            r[++n] = '<tr><th>Title</th><td>' + reference.data.title + '</td></tr>';
            r[++n] = '<tr><th>Frirst Author</th><td>' + reference.data.first_author + '</td></tr>';
            r[++n] = '<tr><th>Authors</th><td>' + reference.data.authors + '</td></tr>';
            r[++n] = '<tr><th>Journal</th><td>' + reference.data.journal + '</td></tr>';
            r[++n] = '<tr><th>Year</th><td>' + reference.data.year + '</td></tr>';
            r[++n] = '<tr><th>Month</th><td>' + reference.data.month + '</td></tr>';
            r[++n] = '<tr><th>Volume</th><td>' + reference.data.volume + '</td></tr>';
            r[++n] = '<tr><th>Pages</th><td>' + reference.data.pages + '</td></tr>';
            r[++n] = '<tr><th>DOI</th><td><a target="_blank" href="' + reference.data.doi + '">' + reference.data.doi + '</a></td></tr>';
            if (ads_or_arxiv != null) {
                r[++n] = '<tr><th>External URL</th><td><a target="_blank" href="' + reference.data.ads_url + '">' + ads_or_arxiv + '</a>'  + '</td></tr>';
            } else {
                r[++n] = '<tr><th>External URL</th><td>---</td></tr>';
            }
            r[++n] = '</tbody>';
            $('#reference').html(r.join('')); 
        }
    });
}

function retrieve_reference_observations(pk) {
    var table = $('#observations' + pk).DataTable({
        'serverside': true,
        'processing': true,
        'language': {
            processing: '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i>'
        },
        'ordering': false,
        'searching': false,
        'ajax': '/api/v1/catalogue/observation/?reference=' + pk + '&format=datatables',
        'columns': [
            {
                'data': 'astro_object.name',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        var altname = '';
                        if(row.astro_object.altname) {
                            altname = ' (' + row.astro_object.altname + ') ';
                        }
                        console.log(altname);
                        data = '<a href="/catalogue/astro_object/' + row.astro_object.slug
                            + '">' + row.astro_object.name + altname + '</a>';
                    }
                    return data;
                }
            },
            { 'data': 'astro_object.altname' },
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
            { 'data': 'sigma_down' }
        ]
    });
};
