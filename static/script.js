document.addEventListener('DOMContentLoaded', function() {
    const useCurrentLocationButton = document.getElementById('use_current_location');
    const startLocationInput = document.getElementById('start_location');

    // Initialize Mapbox Geocoder for the start location input field
    const geocoder = new MapboxGeocoder({
        accessToken: 'YOUR_MAPBOX_ACCESS_TOKEN',
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
