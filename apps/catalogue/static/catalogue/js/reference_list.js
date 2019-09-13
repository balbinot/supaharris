$(document).ready(function() {
    var table = $('#references').DataTable({
        'serverSide': false,
        'processing': true,
        'lengthMenu': [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        'ajax': '/api/v1/catalogue/reference/?format=datatables',
        'order': [[ 1, "desc" ]],
        'columns': [
            {
                'data': 'first_author',
                'render': function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href="' + row.frontend_url + '">' + row.first_author + '</a>';
                    }
                    return data;
                }
            },
            {'data': 'year'},
            {'data': 'title'},
            {
                'data': 'ads_url',
                'render': function(data, type, row, meta){
                    if (row.ads_url.toLowerCase().includes('arxiv.org')) {
                        var ads_or_arxiv = 'arXiv';
                    } else if (row.ads_url.toLowerCase().includes('ads')) {
                        var ads_or_arxiv = 'ADS';
                    } else {
                        return '---';
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

