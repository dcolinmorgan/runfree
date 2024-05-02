document.documentElement.requestFullscreen().catch((e) => {
  console.log(e);
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js').then(function(registration) {
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function(err) {
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
    const moreOptionsToggle = document.getElementById('more_options_toggle');
    const moreOptionsContainer = document.getElementById('more_options_container');

    moreOptionsToggle.addEventListener('click', function() {
        // Toggle the visibility of the more options container
        if (moreOptionsContainer.style.height === '0px' || !moreOptionsContainer.style.height) {
            moreOptionsContainer.style.height = 'auto'; // Expand the container
        } else {
            moreOptionsContainer.style.height = '0px'; // Collapse the container
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const useCurrentLocationButton = document.getElementById('use_current_location');
    const startLocationInput = document.getElementById('start_location');

    // Initialize Mapbox Geocoder for the start location input field
    const geocoder = new MapboxGeocoder({
        accessToken: 'MAPBOX_TOKEN',
        mapboxgl: mapboxgl
    });

    startLocationInput.parentNode.insertBefore(geocoder.onAdd(map), startLocationInput.nextSibling);

    // Add click event listener to the "Use Current Location" button
    useCurrentLocationButton.addEventListener('click', function() {
        // Try to get the current geolocation
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                // Set the value of the start location input field to the current location
                startLocationInput.value = `${currentLocation.lat},${currentLocation.lng}`;
            }, function(error) {
                console.error('Error getting current location:', error);
            });
        } else {
            console.error('Geolocation is not supported by this browser.');
        }
    });
});


