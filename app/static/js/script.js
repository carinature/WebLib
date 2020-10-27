/**
* checkes and unchecks all the items in the serach results (step 1) checklist
* */
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}
/**
* when selecting the Fetch Full Text checkbox this will make the warning paragraph to appear beneath the chek=ckbox
* currently not using this because it makes the filter form look and act funny
* */
function displayWarningFetchAllChkbx() {
  // Get the checkbox
  var checkBox = document.getElementById("fetch_full_chkbox");
  // Get the output text
  var text = document.getElementById("fetch_full_warn");

  // If the checkbox is checked, display the output text
  if (checkBox.checked){
    text.style.display = "block";
  } else {
    text.style.display = "none";
  }
}

