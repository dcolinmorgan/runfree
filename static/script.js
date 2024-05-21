document.addEventListener("DOMContentLoaded", function() {
  // Enable fullscreen
  document.documentElement.requestFullscreen().catch((e) => {
      console.log(e);
  });

  // Register service worker
  if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
          navigator.serviceWorker.register('/service-worker.js').then(function(registration) {
              console.log('ServiceWorker registration successful with scope: ', registration.scope);
          }).catch(function(err) {
              console.log('ServiceWorker registration failed: ', err);
          });
      });
  }

  // Handle form submission for using current location
  document.getElementById("use_current_location").addEventListener("click", function() {
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(function(position) {
              var latitude = position.coords.latitude;
              var longitude = position.coords.longitude;

              // Update start and end location input fields with user's current location
              document.getElementById("start_location").value = latitude + "," + longitude;
          }, function(error) {
              console.error("Error getting current location:", error);
              alert("Error getting current location. Please enter manually.");
          });
      } else {
          alert("Geolocation is not supported by this browser. Please enter manually.");
      }
  });

  // Toggle visibility of more options container
  document.getElementById("more_options_toggle").addEventListener("click", function() {
      var container = document.getElementById("more_options_container");
      container.style.display = container.style.display === "block" ? "none" : "block";
  });
});

$(document).ready(function() {
  // Set the default unit to kilometers
  var unit = "km";
  $("#unit_mi").removeClass("active"); // Ensure miles button is not active by default

  // Function to toggle between kilometers and miles
  $(".unit-button").click(function() {
      $(".unit-button").removeClass("active");
      $(this).addClass("active");
      unit = $(this).text().toLowerCase();
      $("#unit").val(unit);
  });

  // Set the unit value to kilometers initially
  $("#unit").val(unit);

  // Set the default unit to water
  var unit = "water";

  $(".run_to-button").click(function() {
      $(".run_to-button").removeClass("active");
      $(this).addClass("active");
      unit = $(this).text().toLowerCase();
      $("#unit").val(unit);
  });

  // Set the unit value to water initially
  $("#unit").val(unit);

  // jQuery code to toggle display of more options
  $("#more_options_toggle").click(function() {
      $("#more_options_container").toggle();
  });

  // Handle form submission for using current location (jQuery version)
  $("#use_current_location").click(function() {
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(function(position) {
              var latitude = position.coords.latitude;
              var longitude = position.coords.longitude;

              // Update start and end location input fields with user's current location
              $("#start_location").val(latitude + "," + longitude);
          }, function(error) {
              console.error("Error getting current location:", error);
              alert("Error getting current location. Please enter manually.");
          });
      } else {
          alert("Geolocation is not supported by this browser. Please enter manually.");
      }
  });

  var $content = $(".header").next();
  $content.hide();
  $(".header").text("More");

  // Toggle visibility of more options container with slide effect
  $(".header").click(function() {
      var $header = $(this);
      var $content = $header.next();
      $content.slideToggle(500, function() {
          $header.text($content.is(":visible") ? "Less" : "More");
      });
  });
});

// Set dark mode based on system preference
document.addEventListener("DOMContentLoaded", function() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.body.classList.add("dark-mode");
  }

  // Toggle dark mode
  document.getElementById("dark_mode_toggle").addEventListener("click", function() {
      document.body.classList.toggle("dark-mode");
  });
});

document.getElementById('distance').addEventListener('input', function() {
  document.getElementById('distanceValue').textContent = this.value;
});

document.querySelectorAll('.run_to-button').forEach(button => {
  button.addEventListener('click', function(event) {
      var otherLocationField = document.getElementById('other-location-field');
      if (event.target.id === 'other') {
          if (otherLocationField.classList.contains('hidden')) {
              otherLocationField.classList.remove('hidden');
          } else {
              otherLocationField.classList.add('hidden');
          }
      } else {
          otherLocationField.classList.add('hidden');
      }
  });
});

document.getElementById('distance').addEventListener('input', updateLinkText);

function updateLinkText() {
  var distance = document.getElementById('distance').value;
  var unit = document.getElementById('unit').value;
  var runTo = document.querySelector('.run_to-button.active') ? document.querySelector('.run_to-button.active').textContent : '';

  var linkText = 'Random route';
  if (distance && unit && runTo) {
      linkText = `Random ${distance}${unit} route to a ${runTo}`;
  }
  
  document.getElementById('trail-link').textContent = linkText;
}

// Initialize the link text
updateLinkText();
