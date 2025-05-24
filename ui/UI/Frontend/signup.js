// signup.js

// Initialize Google Sign-In
function initGoogleSignIn() {
    gapi.load('auth2', function () {
      const auth2 = gapi.auth2.init({
        client_id: '897940445281-iha9aas64rosuti25itk45er49genlif.apps.googleusercontent.com' // Replace with your actual client ID
      });
      console.log('Google Auth2 Initialized:', auth2);
    });
    function onSignIn(googleUser) {
      var profile = googleUser.getBasicProfile();
      console.log("Name: " + profile.getName());
      console.log("Email: " + profile.getEmail());
    }
  }
  
  // Event listener for DOMContentLoaded to make sure the DOM is loaded first
  document.addEventListener('DOMContentLoaded', function () {
    // Initialize Google Sign-In
    initGoogleSignIn();
  
    // Google Sign-In button click
    document.querySelector('.google-btn').addEventListener('click', async () => {
      try {
        const googleUser = await gapi.auth2.getAuthInstance().signIn();  // Open Google login popup
        const googleToken = googleUser.getAuthResponse().id_token;       // Get token
  
        // Send token to backend
        const response = await fetch('http://localhost:5000/auth/google-login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ googleToken })
        });
  
        const result = await response.json();
  
        if (response.ok) {
          alert(result.message); // Login success
        } else {
          alert('Error: ' + result.message);
        }
      } catch (error) {
        console.error('Google login error:', error);
        alert('Error during Google login.');
      }
    });
  
    // Sign up form submit
    document.getElementById('signupForm').addEventListener('submit', async function (e) {
      e.preventDefault();
  
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
  
      try {
        const response = await fetch('http://localhost:5000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
  
        const result = await response.json();
  
        if (response.ok) {
          alert(result.message);
        } else {
          alert('Error: ' + result.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Error: Could not connect to server.");
      }
    });
  });
  