/**
* checkes and unchecks all the items in the serach results (step 1) checklist
* */
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    for (let i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}
/**
* when selecting the Fetch Full Text checkbox this will make the warning paragraph to appear beneath the chek=ckbox
* currently not using this because it makes the filter form look and act funny
* */
function displayWarningFetchAllChkbx() {
  // Get the checkbox
  let checkBox = document.getElementById("fetch_full_chkbox");
  // Get the output text
  let text = document.getElementById("fetch_full_warn");

  // If the checkbox is checked, display the output text
  if (checkBox.checked){
    text.style.display = "block";
  } else {
    text.style.display = "none";
  }
}


function toggle_show_element_by_id(elm_id) {
  // Get the element
  let elm = document.getElementById(elm_id);

  // If the element is shown, hide it. Otherwise, display
  if ('none'===elm.style.display){
    elm.style.display = "block";
  } else {
    elm.style.display = "none";
  }
}




function more_less_info(btn_id, elm_id) {
  // Get the checkbox
  let btn = document.getElementById(btn_id);
  // Get the element
  let elm = document.getElementById(elm_id);

  // If the element is shown, hide it. Otherwise, display
  if ('none'===elm.style.display){
    elm.style.display = "block";
    btn.childNodes[0].nodeValue = 'Show Less'
  } else {
    elm.style.display = "none";
    btn.childNodes[0].nodeValue = 'Show More'
  }
}

