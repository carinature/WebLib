/**
 * checkes and unchecks all the items in the serach results (step 1) checklist
 * */
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    console.log('==============')
    for (let i = 0, n = checkboxes.length; i < n; i++) {
        let checked = source.checked;
        checkboxes[i].checked = checked;
        if (checked) source.childNodes[0].nodeValue = 'Remove All Selections';
        else source.childNodes[0].nodeValue = 'Select All the Results';

    }
}

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


$('a#test').on('click', function (e) {
    e.preventDefault()
    $.getJSON('fetch_results',
        function (data) {
            //do nothing
        });
    return false;
});


// function more_less_info(btn_id, elm_id, show_msg = 'Show More', hide_msg = 'Show less') {
function more_less_info(btn_id, elm_id, show_msg = '', hide_msg = '') {
    let btn = document.getElementById(btn_id); // Get the checkbox/button
    console.log(btn_id);
    console.log(btn);
    let elm = document.getElementById(elm_id); // Get the element to show/hide
    // If the element is shown, hide it. Otherwise, display
    if ('none' === elm.style.display) {
        elm.style.display = "block";
        elm.style.display = 'inline';
        if (hide_msg) btn.childNodes[0].nodeValue = hide_msg;
    } else {
        elm.style.display = "none";
        if (show_msg) btn.childNodes[0].nodeValue = show_msg;
    }
    if (hide_btn_flag) btn.style.display = "none"
}

function add_field(type = 'include') {
    // which table to expand
    let tbody = document.getElementById(type + 's-0').lastChild;
    // get number of input fields
    let labels = tbody.getElementsByTagName('label');
    let last_label = labels[labels.length - 1];
    let i = 1 + Number(last_label.attributes[0].value.split('-')[1]);
    // too many fields added
    if (2 < i) {
        alert("Hey buddy, you're asking too much.");
        return;
    }
    // construct and add label
    let caps = type.charAt(0).toUpperCase() + type.slice(1);
    let label = document.createElement("label");
    label.setAttribute('for', type + 's-' + i + '-' + type);
    let text = document.createTextNode(caps);
    label.appendChild(text);
    let new_th = document.createElement("th");
    new_th.appendChild(label);
    // construct and add input field
    let new_input = document.createElement("input");
    new_input.setAttribute('id', caps);
    new_input.setAttribute('name', caps);
    new_input.setAttribute('placeholder', ' Subject');
    let new_td = document.createElement("td");
    new_td.appendChild(new_input);
    // construct and add the new input row to the table
    let new_tr = document.createElement("tr");
    new_tr.appendChild(new_th);
    new_tr.appendChild(new_td);
    tbody.appendChild(new_tr);


}