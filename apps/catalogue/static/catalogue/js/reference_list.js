$(document).ready(function() {
    var table = $('#references').DataTable({
        'serverside': true,
        'ajax': '/api/v1/catalogue/reference/?format=datatables',
        'columns': [
            {
                'data': { slug: 'slug', first_author: 'first_author', year: 'year' },
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="/catalogue/reference/' + row.slug + '">' + row.first_author + ' (' + row.year + ')' + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'title'},
            {
                'data': 'ads_url',
                'render': function(data, type, row, meta){
                    if (row.ads_url.toLowerCase().includes('arxiv.org')) {
                        var ads_or_arxiv = 'arXiv';
                    } else if (row.ads_url.toLowerCase().includes('ads')) {
                        var ads_or_arxiv = 'ADS';
                    } else {
                        var ads_or_arxiv = 'URL';
                    }
                    
                    if(type === 'display'){
                        data = '<a target="_blank" href="' + data + '">' + ads_or_arxiv + '</a>';
                    }
                    return data;
                }
            },
        ]
    });
});

