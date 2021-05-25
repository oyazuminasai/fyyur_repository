window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

delete_btn = document.getElementById("delete_btn");
try {
  delete_btn.onclick = function(e){
    venue_id = e.target.dataset['id'];
    fetch('/venues/' + venue_id, {
      method:'DELETE'
    }).then(function(response){
      return response.json();
    }).then( function(jsonResponse){
      location.replace(jsonResponse['url'])
    });
  } 
} catch (error) {
  console.log(error)
}
