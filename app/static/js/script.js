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


function more_less_info(btn_id, elm_id, show_msg = 'Show More', hide_msg = 'Show less') {
    let btn = document.getElementById(btn_id); // Get the checkbox/button
    console.log(btn_id)
    console.log(btn)
    let elm = document.getElementById(elm_id); // Get the element to show/hide
    // If the element is shown, hide it. Otherwise, display
    if ('none' === elm.style.display) {
        elm.style.display = "block";
        if (hide_msg) btn.childNodes[0].nodeValue = hide_msg;
    } else {
        elm.style.display = "none";
        if (show_msg) btn.childNodes[0].nodeValue = show_msg;
    }
    if (hide_btn_flag) btn.style.display = "none"
}

