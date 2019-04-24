$(document).ready(function () {
    $.typeahead({
        input: '#globalSearch',
        callback: {
            onInit: function (node) {
                console.log('Typeahead Initiated on ' + node.selector);
            }
        }
    });
});
