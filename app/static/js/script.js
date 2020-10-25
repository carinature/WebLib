
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}