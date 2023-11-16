// (function() {

//     const idleDurationSecs = 60;    // X number of seconds
//     const redirectUrl = 'http://127.0.0.1:5000/login';  // Redirect idle users to this URL
//     let idleTimeout; // variable to hold the timeout, do not modify

//     const resetIdleTimeout = function() {

//         // Clears the existing timeout
//         if(idleTimeout) clearTimeout(idleTimeout);

//         // Set a new idle timeout to load the redirectUrl after idleDurationSecs
//         idleTimeout = setTimeout(() => location.href = redirectUrl, idleDurationSecs * 1000);
//     };

//     // Init on page load
//     resetIdleTimeout();

//     // Reset the idle timeout on any of the events listed below
//     ['click', 'touchstart', 'mousemove'].forEach(evt => 
//         document.addEventListener(evt, resetIdleTimeout, false)
//     );

// })();


//   // Set the idle time in milliseconds (1 minute in this example)
//   var idleTime = 10000; // 1 minute

//   // Variables to track user activity
//   var idleTimer;
//   var isModalActive = false;

//   function showModal() {
//     // Show the custom modal and overlay
//     document.getElementById('customModal').style.display = 'block';
//     document.getElementById('overlay').style.display = 'block';
//     isModalActive = true;
//   }

//   function resetIdleTimer() {
//     // Reset the idle timer
//     clearTimeout(idleTimer);
//     idleTimer = setTimeout(showModal, idleTime);
//   }

//   function closeAndReset() {
//     // Close the custom modal and overlay
//     document.getElementById('customModal').style.display = 'none';
//     document.getElementById('overlay').style.display = 'none';
//     isModalActive = false;

//     // Reset the idle timer
//     resetIdleTimer();
//   }

//   function redirectToHome() {
//     // Redirect to the home page or perform other actions
//     window.location.href = "your_home_url_here";
//   }

//   // Event listeners for user activity
//   document.addEventListener('mousemove', function() {
//     if (!isModalActive) {
//       resetIdleTimer();
//     }
//   });

//   document.addEventListener('keydown', function() {
//     if (!isModalActive) {
//       resetIdleTimer();
//     }
//   });

//   // Initial setup
//   resetIdleTimer();



// Set the idle time in milliseconds (1 minute in this example)
  var idleTime = 10000; // 1 minute
  var redirectTime = 20000; // 2 minutes (adjust as needed)

  // Variables to track user activity
  var idleTimer;
  var redirectTimer;

  function showModal() {
    // Show the custom modal and overlay
    document.getElementById('customModal').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
  }

  function resetIdleTimer() {
    // Reset the idle timer
    clearTimeout(idleTimer);
    idleTimer = setTimeout(showModal, idleTime);
  }

  function redirectToHome() {
    // Redirect to the home page or perform other actions
    window.location.href = 'http://127.0.0.1:5000/login';;
  }

  function closeAndReset() {
    // Close the custom modal and overlay
    document.getElementById('customModal').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';

    // Reset the idle timer
    resetIdleTimer();
  }

  function checkRedirectTime() {
    // Check if redirect time has elapsed
    redirectTimer = setTimeout(redirectToHome, redirectTime);
  }

  // Event listeners for user activity
  document.addEventListener('mousemove', function() {
    resetIdleTimer();
    clearTimeout(redirectTimer); // Reset redirect timer on user activity
  });

  document.addEventListener('keydown', function() {
    resetIdleTimer();
    clearTimeout(redirectTimer); // Reset redirect timer on user activity
  });

  // Initial setup
  resetIdleTimer();
  checkRedirectTime();
