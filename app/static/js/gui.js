/**
 * When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
 * */
window.onscroll = function () {
    scrollFunction()
};

function scrollFunction() {
    let navbar = document.getElementsByClassName("navbar")[0];
    let navbar_brand = document.getElementsByClassName("navbar-brand")[0];
    let logo = document.getElementById("logo");
    let button_line = document.getElementById("navbarResponsive");
    let subtitle = document.getElementById("navbar-subtitle");
    let title = document.getElementsByClassName("navbar-title")[0];

    if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
        document.getElementById("top_btn").style.display = "block";

    } else if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {

        // scrolled DOWN
        title.style.padding = "1em 0 0 0 ";
        title.style.fontSize = '0.5em';

        navbar.style.padding = "0";
        navbar.style.margin = "0";

        navbar_brand.style.padding = "0";
        // navbar_brand.style.margin = "0";

        logo.style.margin = ".5rem";

        // subtitle.style.display = 'none';
        // subtitle.style.transition = '400ms';
        // title.style.transform = "scale(0.5)";

    } else {
        // scrolled to TOP
        document.getElementById("top_btn").style.display = "none";
        title.style.padding = "initial";
        title.style.fontSize = 'inherit';

        // navbar_brand.style.margin=".3125rem 1rem .3125rem 0 ";
        navbar.style.padding = ".8em";

        navbar_brand.style.padding = "0.3125em 0";
        // navbar_brand.style.marginRight = ".8em";

        // logo.style.margin = "30px 10px 30px 10px";
        logo.style.height = "2.5em";
        logo.style.margin = "1em";

        // subtitle.style.display = 'block';
        // subtitle.style.transition = '400ms';
        // title.style.transform = "scale(1)";
    }
}

/**
 * When the user clicks on the button, scroll to the top of the document
 * */
// $('button#csv_to_mysql_btn').on('click', function () {
$(document).ready(function () {
    $("#top_btn").click(function () {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    });
});

/** supposed to toggle between to radio button options */
$('input.inline-radio').on('click', function () {
    console.log('jdfhkjasdhflkjasdhf');
    console.log(this);
    let chkYes = document.getElementById("chkYes");
    let search_subject = document.getElementById("search-subject");
    let search_ref = document.getElementById("search-ref");
    search_subject.style.display = chkYes.checked ? "block" : "none";
    search_ref.style.display = chkYes.checked ? "none" : "block";
    console.log(search_ref.style.display)
});


/**
 * checkes and unchecks all the items in the serach results (step 1) checklist
 * */
function filter_check_all(source) {
    checkboxes = document.getElementsByName('filter-opt');
    console.log('==============');
    for (let i = 0, n = checkboxes.length; i < n; i++) {
        let checked = source.checked;
        checkboxes[i].checked = checked;
        if (checked) source.childNodes[0].nodeValue = 'Remove All Selections';
        else source.childNodes[0].nodeValue = 'Select All the Results';

    }
}

/*
    Enable popovers via JavaScript:
*/
// $('#example').popover(options)

/** creates a popover (small window hovering) when hovering over the div*/
$(function () {
    $('.popover_category').hover(
        function (event) {
            // mouse in event handler
            let elem = $(event.currentTarget);
            let href = elem[0].getAttribute('href')
            let id = elem[0].id
            let data = 'reference is tagged with the subject '
            if ('#high' === href || 'high' === id) {
                data += 'in more than one book';
            }
            if ('#valid' === href || 'valid' === id) {
                data += 'only in one book, but more than once';
            }
            if ('#not' === href || 'not' === id) {
                data += 'only once, in one book';
            }
            elem.popover({
                trigger: 'manual',
                html: true,
                animation: true,
                container: elem,
                content: data,
                placement: 'top'
            }).popover('show');
        },
        function (event) {
            // mouse out event handler
            var elem = $(event.currentTarget);
            // elem.popover('dispose');
            elem.popover('hide');
        }
    )
});

/****************************************************
 ****************************************************
 *        For DBG      fixme remove in production
 *****************************************************
 *****************************************************/
/*
// $('button#csv_to_mysql_btn').on('click', function () {
$(document).ready(function () {
    $("#refreshCSS").click(function () {
        css_refresh_sdfsadfsaf()
    });
});
*/
