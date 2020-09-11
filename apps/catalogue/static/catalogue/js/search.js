$(document).ready(function () {
    // Get saved astroObjectNames from sessionStorage, or set it
    astroObjectNames = JSON.parse(sessionStorage.getItem('astroObjectNames'));
    if (astroObjectNames == null) {
        var astroObjectNames = getAstroObjectNames();
    } else {
        var expected;
        $.ajax({
            type: 'GET',
            async: false,
            dataType: 'json',
            url: '/api/v1/catalogue/astro_object/?format=json',
            success: function(data) {
                expected = data['count'];
            },
        });
        console.log('# astroObjectNames expected =', expected);
        console.log('# astroObjectNames found    =', Object.keys(astroObjectNames).length)
        if(Object.keys(astroObjectNames).length != expected) {
            var astroObjectNames = getAstroObjectNames();
        } else {
            console.log("Using astroObjectNames from sessionStorage.")
        }
    }
    autocomplete(document.getElementById('globalSearch'), astroObjectNames);
});


function getAstroObjectNames(url, currentCount, astroObjectNames) {
    console.log( 'Calling getAstroObjectNames ...' );
    url = (typeof url !== 'undefined') ?  url : '/api/v1/catalogue/astro_object/?format=json';
    currentCount = (typeof currentCount !== 'undefined') ?  currentCount : 0;
    astroObjectNames = (typeof astroObjectNames !== 'undefined') ?  astroObjectNames : {};

    $.ajax({
        type: 'GET',
        async: true,
        dataType: 'json',
        url: url,
        success: function(data) {
            var totalCount = data['count'];
            data['results'].forEach(function(row, i) {
              astroObjectNames[row.name] = row.frontend_url;
              if(row.altname !== null){
                  // astroObjectNames[row.altname] = row.frontend_url;
                  console.log('TODO: altname', row.altname);
              }
            });
            currentCount = Object.keys(astroObjectNames).length;
            console.log( 'getAstroObjectNames --> GET retrieved', currentCount, '/', totalCount, 'instances.' );

            if (data['next'] != 'null') {
                return getAstroObjectNames(data['next'], currentCount, astroObjectNames);
            };
        },
    });

    // Save astroObjectNames to sessionStorage
    console.log( 'Saving astroObjectNames to sessionStorage.');
    sessionStorage.setItem('astroObjectNames', JSON.stringify(astroObjectNames));
    return astroObjectNames;
};


function autocomplete(inp, astroObjectNames) {
    var arr = Object.keys(astroObjectNames);
    var currentFocus;
    /* execute a function when someone writes in the text field: */
    inp.addEventListener('input', function(e) {
        var a, b, i, val = this.value;
        /* close any already open lists of autocompleted values */
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /* create a div element that will contain the items (values): */
        a = document.createElement('div');
        a.setAttribute('id', this.id + 'autocomplete-list');
        a.setAttribute('class', 'autocomplete-items');
        /* append the div element as a child of the autocomplete container: */
        this.parentNode.appendChild(a);
        /* for each item in the array... */
        for (i = 0; i < arr.length; i++) {
            /* check if the item starts with the same letters as the text field value: */
            // TODO: implement fuzzy matching, and split on ' ' (e.g. 'NGC 104')
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /* create a div element for each matching element: */
                b = document.createElement('div');
                /* make the matching letters bold: */
                b.innerHTML = '<strong>' + arr[i].substr(0, val.length) + '</strong>';
                b.innerHTML += arr[i].substr(val.length);
                /* insert a input field that will hold the current array item's value: */
                b.innerHTML += '<input type="hidden" value="' + arr[i] + '">';
                /* execute a function when someone clicks on the item value (div element): */
                b.addEventListener('click', function(e) {
                    inp.value = this.getElementsByTagName('input')[0].value;

                    // Redirect to the frontend_url of the given AstroObject
                    window.location.href = astroObjectNames[inp.value];
                    /* close the list of autocompleted values,
              (or any other open lists of autocompleted values: */
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    /* execute a function presses a key on the keyboard: */
    inp.addEventListener('keydown', function(e) {
        var x = document.getElementById(this.id + 'autocomplete-list');
        if (x) x = x.getElementsByTagName('div');
        if (e.keyCode == 40) {
            /* If the arrow DOWN key is pressed,
             * increase the currentFocus variable: */
            currentFocus++;
            /* and and make the current item more visible: */
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /* If the arrow UP key is pressed,
             * decrease the currentFocus variable: */
            currentFocus--;
            /* and and make the current item more visible: */
            addActive(x);
        } else if (e.keyCode == 13) {
            /* If the ENTER key is pressed, prevent the form from being submitted, */
            e.preventDefault();
            if (currentFocus > -1) {
                /* and simulate a click on the 'active' item: */
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /* a function to classify an item as 'active': */
        if (!x) return false;
        /* start by removing the 'active' class on all items: */
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /* add class 'autocomplete-active': */
        x[currentFocus].classList.add('autocomplete-active');
    }
    function removeActive(x) {
        /* a function to remove the 'active' class from all autocomplete items: */
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove('autocomplete-active');
        }
    }
    function closeAllLists(elmnt) {
        /* close all autocomplete lists in the document,
         * except the one passed as an argument: */
        var x = document.getElementsByClassName('autocomplete-items');
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /* execute a function when someone clicks in the document: */
    document.addEventListener('click', function (e) {
        closeAllLists(e.target);
    });
}
