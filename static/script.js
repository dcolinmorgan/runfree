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

// Function to handle form submission
document.addEventListener("DOMContentLoaded", function() {
        document.getElementById("use_current_location").addEventListener("click", function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    var latitude = position.coords.latitude;
                    var longitude = position.coords.longitude;

                    // Update start and end location input fields with user's current location
                    document.getElementById("start_location").value = latitude + "," + longitude;
                    document.getElementById("end_location").value = latitude + "," + longitude;
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

// // Function to handle form submission
// document.addEventListener("DOMContentLoaded", function() {
//       document.getElementById("use_current_location").addEventListener("click", function() {
//           if (navigator.geolocation) {
//               navigator.geolocation.getCurrentPosition(function(position) {
//                   var latitude = position.coords.latitude;
//                   var longitude = position.coords.longitude;

//                   // Update start and end location input fields with user's current location
//                   document.getElementById("start_location").value = latitude + "," + longitude;
//                   document.getElementById("end_location").value = latitude + "," + longitude;
//               }, function(error) {
//                   console.error("Error getting current location:", error);
//                   alert("Error getting current location. Please enter manually.");
//               });
//           } else {
//               alert("Geolocation is not supported by this browser. Please enter manually.");
//           }
//       });

// Toggle visibility of more options container
      document.getElementById("more_options_toggle").addEventListener("click", function() {
          var container = document.getElementById("more_options_container");
          container.style.display = container.style.display === "block" ? "none" : "block";
      });
  });

  // jQuery code to toggle display of more options
  $(document).ready(function() {
      $("#more_options_toggle").click(function() {
          $("#more_options_container").toggle();
      });
  });


// // Function to handle form submission
// document.addEventListener("DOMContentLoaded", function() {
//         document.getElementById("use_current_location").addEventListener("click", function() {
//             if (navigator.geolocation) {
//                 navigator.geolocation.getCurrentPosition(function(position) {
//                     var latitude = position.coords.latitude;
//                     var longitude = position.coords.longitude;

//                     // Update start and end location input fields with user's current location
//                     document.getElementById("start_location").value = latitude + "," + longitude;
//                     document.getElementById("end_location").value = latitude + "," + longitude;
//                 }, function(error) {
//                     console.error("Error getting current location:", error);
//                     alert("Error getting current location. Please enter manually.");
//                 });
//             } else {
//                 alert("Geolocation is not supported by this browser. Please enter manually.");
//             }
//         });

//         // Toggle visibility of more options container
//         document.getElementById("more_options_toggle").addEventListener("click", function() {
//             var container = document.getElementById("more_options_container");
//             container.style.display = container.style.display === "block" ? "none" : "block";
//         });
//     });
