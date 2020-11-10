// When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
window.onscroll = function () {
    scrollFunction()
};

function scrollFunction() {
    let navbar = document.getElementsByClassName("navbar")[0];
    let logo = document.getElementById("logo");
    let button_line = document.getElementById("navbarResponsive");
    let subtitle = document.getElementById("navbar-subtitle");
    let title = document.getElementsByClassName("navbar-title")[0];

    if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
        document.getElementById("myBtn").style.display = "block";

        // scrolled DOWN
        // subtitle.style.display = 'none';
        // subtitle.style.transition = '400ms';
        // navbar.style.padding = "5px 10px 5px 10px";
        // logo.style.height = "3rem";
        // title.style.transform = "scale(0.5)";
        // title.style.margin = "0";
        // title.style.paddingTop = "0";


        // logo.style.margin = "0";
        // logo.style.width = "5em";
        // navbar.style.padding = "0";
        // logo.style.padding = "5px 10px 5px 10px";
        // logo.style.margin = "5px 10px 5px 10px";
        title.style.padding = "1rem 0 0 0 ";
        title.style.fontSize = '0.5em';

    } else {  // scrolled to TOP
        document.getElementById("myBtn").style.display = "none";

        // subtitle.style.display = 'block';
        // subtitle.style.transition = '400ms';

        // logo.style.height = "3rem";
        // title.style.transform = "scale(1)";


        // navbar.style.padding = "30px 10px 10px 10px";
        // logo.style.padding = "30px 10px 30px 10px";
        // logo.style.margin = "30px 10px 30px 10px";
        // logo.style.width = "10em";
        title.style.padding = "initial";
        title.style.fontSize = 'inherit';
    }
}


// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}


function ShowHideDiv() {
    let chkYes = document.getElementById("chkYes");
    let search_subject = document.getElementById("search-subject");
    let search_ref = document.getElementById("search-ref");
    search_subject.style.display = chkYes.checked ? "block" : "none";

    search_ref.style.display = chkYes.checked ? "none" : "block";
}

