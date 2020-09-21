function get_joke_of_the_day() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            // Access the result here
            alert(this.responseText);
        }
    };
    xhttp.open("GET", "https://api.jokes.one/jod?category=animal", true);
    xhttp.setRequestHeader("Content-type", "app/json");
    xhttp.setRequestHeader("X-JokesOne-Api-Secret", "YOUR API HERE");
    xhttp.send();
}

function search_button_function() {
    console.log("search-button");
    // let anchor = document.getElementById("action-area");
    // console.log(anchor);
    // let htmlelem = "<h1>htmlelem</h1>";
    // anchor.insertAdjacentHTML("afterend", htmlelem);
    // let elem = document.createElement('h2');
    // elem = anchor.insertAdjacentElement("afterend", elem);
    // elem.textContent = 'pipi';

      location.replace("search-results")
      // location.replace("search-results.html")

}

function filter_check_all(source) {
  checkboxes = document.getElementsByName('filter-opt');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}