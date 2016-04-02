      // This example requires the Places library. Include the libraries=places
      // parameter when you first load the API. For example:
      // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 39.949, lng: -75.181},
          zoom: 13
        });
        var input = /** @type {!HTMLInputElement} */(
            document.getElementById('pac-input'));

        var types = document.getElementById('type-selector');
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(types);

        var autocomplete = new google.maps.places.Autocomplete(input);
        autocomplete.bindTo('bounds', map);

        var infowindow = new google.maps.InfoWindow();
        var marker = new google.maps.Marker({
          map: map,
          anchorPoint: new google.maps.Point(0, -29)
        });

        autocomplete.addListener('place_changed', function() {
          infowindow.close();
          marker.setVisible(false);
          var place = autocomplete.getPlace();
          if (!place.geometry) {
            window.alert("Autocomplete's returned place contains no geometry");
            return;
          }

          // If the place has a geometry, then present it on a map.
          if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
          } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);  // Why 17? Because it looks good.
          }
          marker.setIcon(/** @type {google.maps.Icon} */({
            url: place.icon,
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(35, 35)
          }));
          marker.setPosition(place.geometry.location);
          marker.setVisible(true);

          var address = '';
          if (place.address_components) {
            address = [
              (place.address_components[0] && place.address_components[0].short_name || ''),
              (place.address_components[1] && place.address_components[1].short_name || ''),
              (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');
          }

          infowindow.setContent('<div><strong>' + place.name + '</strong><br>' + address);
          infowindow.open(map, marker);
        });

        // Sets a listener on a radio button to change the filter type on Places
        // Autocomplete.
        function setupClickListener(id, types) {
          var radioButton = document.getElementById(id);
          radioButton.addEventListener('click', function() {
            autocomplete.setTypes(types);
          });
        }

        setupClickListener('changetype-all', []);
        setupClickListener('changetype-address', ['address']);
        setupClickListener('changetype-establishment', ['establishment']);

        $.ajax({
          type: "GET",
          url: "/get-resource"
        }).done(function(data){
            data = JSON.parse(data)
            for(var i = 0; i < data.length; i++){
            //we have the pins data, access it here and place pins on map
              latLng = new google.maps.LatLng(data[i].Latitude, data[i]
              .Longitude)
              var marker = new google.maps.Marker({
                position: latLng,
                map: map,
                visible: true,
                title: data[i].Name
              });

              var infowindow = new google.maps.InfoWindow({
                content: 'i cannot get this'
              });

              var expandedwindow = new google.maps.InfoWindow({
                content: '<div id="content">'+
                  '<p><b>'+ data[i].Name +'</b></p>'+
                  '</div>'
              });

              marker.addListener('click', function() {
                var json_data = {
                    csrf_token: $('meta[name="csrf-token"]').prop('content'),
                    data: data[i].Name
                };
                console.log(data[i].Name)
                $.post("/get-info", json_data)
                .done(function() {
                    console.log('success');
                }).fail(function() {
                    console.log('fail');
                });
                //expandedwindow.setContent()
                expandedwindow.open(map, this);
              });

              marker.setMap(map);
             }
         })
      }

