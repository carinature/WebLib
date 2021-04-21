//for testing purposes - currently not used
$('a#test').on('click', function (e) {
    e.preventDefault();
    $.getJSON('fetch_results',
        function (data) {
            //do nothing
        });
    return false;
});

//for testing purposes - currently not used
$('a#test_query').on('click', function (e) {
    e.preventDefault();
    let json_res = $.getJSON('flam_flam',
        function (data) {
            //do nothing
            console.log('datatatatata');
            console.log(data);

        });
    console.log('json_res', json_res);
    console.log('json_res', json_res);
    return false;
});

//for testing purposes - currently not used(?)
$('button#js-to-py').on('click', function (e) {
    //  NEXT TO COMMANDS DO NOT SEEM TO WORK
    alert("You pushed the button  =)")
    console.log("You pushed the button  =)")
    e.preventDefault();
    $.getJSON('flask_route_but_not_webpage',
        function (data) {
            //do nothing
        });
    return false;
});
/** template example **/
$(document).ready(function () {
    $("#linkid").click(function () {
        dothings();
    });
});

//load raw scv files into the MySQL DB
$('button#csv_to_mysql_btn').on('click', function (e) {
    alert("You are about to ask the server to load raw scv files into the mysql DB. " +
        "It's gonna take a loooong time to finish (if lucky). " +
        "Are you sure?")
    console.log("Loading DataBase ... ")
    console.log("It's happening ... ")
    e.preventDefault();
    $.getJSON('csv_to_mysql_func',
        function (data) {
            //do nothing
        });

    return false;
});

// todo should load an email to the db?
$('button#email_button').on('click', function (e) {
    //  NEXT TO COMMANDS DO NOT SEEM TO WORK
    alert("Adding your Email address")
    e.preventDefault();
    $.getJSON('falala',
        function (data) {
            //do nothing
        });
    return false;
});

// function more_less_info(btn_id, elm_id, show_msg = 'Show More', hide_msg = 'Show less') {
function more_less_info(btn_id, elm_id, show_msg = '', hide_msg = '', hide_btn_flag=false) {
    let btn = document.getElementById(btn_id); // Get the checkbox/button
    let elm = document.getElementById(elm_id); // Get the element to show/hide
    // If the element is shown, hide it. Otherwise, display
    if ('none' === elm.style.display) {
        // elm.style.display = "block";
        elm.style.display = 'inline';
        if (hide_msg) btn.childNodes[0].nodeValue = hide_msg;
    } else {
        elm.style.display = "none";
        if (show_msg) btn.childNodes[0].nodeValue = show_msg;
    }
    if (hide_btn_flag) btn.style.display = "none";
}

/**
 * adding a field to the filtering form
 * */
$('button.add-btn').on('click', function (e) {
// function add_field(type = 'exclude') {
    let type = this.id.split('-')[1];
    console.log(type)
    // which table to expand
    let tbody = document.getElementById(type + 's-0').lastChild;
    // get number of input fields
    let labels = tbody.getElementsByTagName('label');
    let i = 0;
    if (0 < labels.length) {
        let last_label = labels[labels.length - 1];
        i = 1 + Number(last_label.attributes[0].value.split('-')[1]);
    }
    // too many fields added
    if (2 < i) {
        alert("Hey buddy, you're asking too much.");
        return;
    }
    // construct and add label
    let id = type + 's-' + i + '-' + type;
    let label = document.createElement("label");
    label.setAttribute('for', id);
    let text = document.createTextNode(type.charAt(0).toUpperCase() + type.slice(1));
    label.appendChild(text);
    let new_th = document.createElement("th");
    new_th.appendChild(label);
    // construct and add input field
    let new_input = document.createElement("input");
    new_input.setAttribute('id', id);
    new_input.setAttribute('name', id);
    new_input.setAttribute('placeholder', ' Subject');
    new_input.setAttribute('style', 'margin-left:15px');
    let new_td = document.createElement("td");
    new_td.appendChild(new_input);
    // construct and add the new input row to the table
    let new_tr = document.createElement("tr");
    new_tr.appendChild(new_th);
    new_tr.appendChild(new_td);
    tbody.appendChild(new_tr);

});

/**
 * The button disappears when you click it
 * */
$('button.disappring-btn').on('click', function (e) {
    this.style.display = 'none';
});

/**
 * clearing all fields in the search bar and filter form
 * */
$('button#clear-filter').on('click', function (e) {
    // reset all drop-down manues
    $("select").each(function () {
        this.selectedIndex = 0
    });
    // remove all excess text input fields
    let includes = document.getElementsByTagName('tr');
    console.log(includes)
    // for some reason this worked weird when going from first to last
    for (let j = includes.length - 1; j >= 0; --j) {
        includes[j].remove();
    }
    // clear input
    $("input").each(function () {
        // clear all checkbox fields
        if ('checkbox' === this.type) {
            this.checked = false;
        }
        // clear all text input fields
        if ('text' === this.type) {
            this.value = '';
        }
    });
    add_field('include');
    add_field('exclude');

});

/**
 * clearing all fields in the search bar and filter form
 * */
$('input#fetch_full_chkbox').on('click', function (e) {
    alert('Attention! Checking this box will attempt full text fetching, which can result in very highly loading times.')
});

/**
 * when selecting the Fetch Full Text checkbox this will make the warning paragraph to appear beneath the chek=ckbox
 * currently not using this because it makes the filter form look and act funny
 * */
function displayWarningFetchAllChkbx() {
    let checkBox = document.getElementById("fetch_full_chkbox"); // Get the checkbox
    let text = document.getElementById("fetch_full_warn"); // Get the output text

    // If the checkbox is checked, display the output text
    if (checkBox.checked) text.style.display = "block";
    else text.style.display = "none";
}

$(document).ready(function () {
    $("#linkid").click(function () {
        dothings();
    });
});

// Invoking a python script on click of html button can be accomplished using python-django framework.
// The ajax for it is written this way
// <input type = “button” id=”b1″ value=”1″>
// <script>
// $(document).ready(function () {
//     $("#b1").click(function () {
//         $.ajax({
//             method: "GET",
//             url: "type your python script path here",
//             data: {"place": value},
//             dataType: "text",
//             success: function (result) {
//                 let data = JSON.parse(result);
//                 console.log(result);
//             }
//         });
//     });
// });
// </script>


//
// function searchjs(srchwrd) {
//     srchwrd = srchwrd.replace('\'', '');
//     console.log(srchwrd);
//     // $.getJSON('flam',
//     // function (data) {
//     //     //do nothing
//     // });
//     $.ajax({
//         method: "post",
//         url: "/search-results",
//         data: 696969,
//         // data: {"place": 'value'},
//         dataType: "text",
//         success: function (result) {
//             let data = JSON.parse(result);
//             console.log(result);
//         }
//     });
// }
