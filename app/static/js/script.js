
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}

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

