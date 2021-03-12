var map_markers = [];
    var data = {{ data | safe}}
    var center_lat = {{ center_lat }}
    var center_lng = {{ center_lng }}
    const myLatLng = {lat: 52.3675734, lng: 4.97};


    function initMap() {
      const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: {lat: center_lat, lng: center_lng},
      });
      for (i = 0; i < data.length; i++) {
      var latlongpair = {lat: data[i]['lat'], lng: data[i]['long']};
      console.log(latlongpair);

      // This event listener calls addMarker() when the map is clicked.
      google.maps.event.addListener(map, "click", (event) => {
        addMarker(event.latLng, map);
      });

      const image ="static/images/mealappicon.png";
      new google.maps.Marker({
        position: latlongpair,
        map,
        title: data[i]['title'],
        icon: image,
      });
      }
}