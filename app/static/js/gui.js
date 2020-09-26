// When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
window.onscroll = function () {
    scrollFunction()
};

function scrollFunction() {
    let navbar = document.getElementsByClassName("navbar")[0];
    let logo = document.getElementById("logo");
    let button_line = document.getElementById("navbarResponsive");
    let title = document.getElementsByClassName("navbar-title")[0];

    if (document.body.scrollTop > 80 || document.documentElement.scrollTop > 80) {
        navbar.style.padding = "5px 10px 5px 10px";
        // navbar.style.padding = "0";

        // logo.style.padding = "5px 10px 5px 10px";
        // logo.style.margin = "5px 10px 5px 10px";
        logo.style.height = "3rem";
        // logo.style.margin = "0";
        // logo.style.width = "5em";
        title.style.transform = "scale(0.5)";
        title.style.margin = "0";
        title.style.paddingTop = "0";
        // title.style.padding = "5px 10px 5px 10px";
        // document.getElementById("navbar-title").style.fontSize = "1em";
        // document.getElementById("subtitle").style.fontSize = "1em"; todo should be smaller?

    } else {
        // navbar.style.padding = "30px 10px 10px 10px";

        // logo.style.padding = "30px 10px 30px 10px";
        // logo.style.margin = "30px 10px 30px 10px";
        logo.style.height = "3rem";
        // logo.style.width = "10em";

        title.style.transform = "scale(1)";
        // title.style.padding = "30px 10px 10px 10px";
        // document.getElementById("navbar-title").style.fontSize = "2em";
        // document.getElementById("subtitle").style.fontSize = "1em"; todo should be smaller?
    }
}


function ShowHideDiv() {
    let chkYes = document.getElementById("chkYes");
    let search_subject = document.getElementById("search-subject");
    let search_ref = document.getElementById("search-ref");
    search_subject.style.display = chkYes.checked ? "block" : "none";

    search_ref.style.display = chkYes.checked ? "none" : "block";
}

