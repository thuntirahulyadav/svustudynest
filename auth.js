// Common Authentication Script for SVUSTUDYNEST
// This file contains all authentication-related functions

// Enhanced authentication check function
async function checkAuthentication() {
  try {
    const response = await fetch('/check-auth', {
      method: 'GET',
      credentials: 'include', // Include cookies for session
      cache: 'no-cache' // Prevent caching
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.authenticated) {
        // Update localStorage with server session data
        localStorage.setItem('studentName', data.student_name);
        localStorage.setItem('studentRoll', data.student_roll);
        localStorage.setItem('isAuthenticated', 'true');
        return true;
      }
    }
    
    // Not authenticated, redirect to login
    localStorage.clear();
    // Clear browser history to prevent back button access
    window.history.replaceState(null, '', '/login.html');
    window.location.href = '/login.html';
    return false;
  } catch (error) {
    console.error('Authentication check failed:', error);
    localStorage.clear();
    window.history.replaceState(null, '', '/login.html');
    window.location.href = '/login.html';
    return false;
  }
}

// Create and show logout confirmation dialog
function showLogoutConfirmation() {
  // Create modal overlay
  const overlay = document.createElement('div');
  overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  overlay.id = 'logoutOverlay';
  
  // Create modal content
  const modal = document.createElement('div');
  modal.className = 'bg-white rounded-lg p-6 max-w-sm w-full mx-4 shadow-xl';
  
  // Modal content
  modal.innerHTML = `
    <div class="text-center">
      <h3 class="text-2xl font-semibold text-gray-900 mb-4">Logout Confirmation</h3>
      <p class="text-gray-600 mb-6">Do you want to logout?</p>
      <div class="flex gap-3 justify-center">
        <button id="logoutYes" class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition">Yes</button>
        <button id="logoutNo" class="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition">No</button>
      </div>
    </div>
  `;
  
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  
  // Add event listeners
  document.getElementById('logoutYes').addEventListener('click', async function() {
    try {
      await fetch('/logout', {
        method: 'POST',
        credentials: 'include',
        cache: 'no-cache'
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.clear();
    
    // Clear browser history and prevent back button access
    window.history.replaceState(null, '', '/login.html');
    window.location.replace('/login.html'); // Use replace instead of href
  });
  
  document.getElementById('logoutNo').addEventListener('click', function() {
    document.body.removeChild(overlay);
  });
  
  // Close modal when clicking outside
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      document.body.removeChild(overlay);
    }
  });
  
  // Close modal with Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const existingOverlay = document.getElementById('logoutOverlay');
      if (existingOverlay) {
        document.body.removeChild(existingOverlay);
      }
    }
  });
}

// Initialize authentication on page load
async function initAuthentication() {
  // Check authentication on page load
  const isAuthenticated = await checkAuthentication();
  if (!isAuthenticated) {
    // This will redirect to login, so we don't need to do anything else
    return;
  }
  
  // Display student name if element exists
  const studentNameElement = document.getElementById('studentName');
  if (studentNameElement) {
    const studentName = localStorage.getItem('studentName');
    studentNameElement.textContent = `Welcome, ${studentName}`;
  }
  
  // Setup logout functionality if logout button exists
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function() {
      showLogoutConfirmation();
    });
  }
  
  // Check authentication periodically (every 2 minutes)
  setInterval(checkAuthentication, 2 * 60 * 1000);
  
  // Prevent back button access after logout
  window.addEventListener('pageshow', function(event) {
    // Check if page is loaded from cache (back button)
    if (event.persisted) {
      checkAuthentication();
    }
  });
  
  // Additional check on page focus (when user returns to tab)
  window.addEventListener('focus', function() {
    checkAuthentication();
  });
}

// Function to check if user is logged in (for conditional rendering)
async function isLoggedIn() {
  try {
    const response = await fetch('/check-auth', {
      method: 'GET',
      credentials: 'include',
      cache: 'no-cache'
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.authenticated;
    }
    return false;
  } catch (error) {
    console.error('Login check failed:', error);
    return false;
  }
}

// Function to get current user info
async function getCurrentUser() {
  try {
    const response = await fetch('/check-auth', {
      method: 'GET',
      credentials: 'include',
      cache: 'no-cache'
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.authenticated) {
        return {
          name: data.student_name,
          roll: data.student_roll
        };
      }
    }
    return null;
  } catch (error) {
    console.error('Get user info failed:', error);
    return null;
  }
}

// Function to logout user
async function logout() {
  try {
    await fetch('/logout', {
      method: 'POST',
      credentials: 'include',
      cache: 'no-cache'
    });
  } catch (error) {
    console.error('Logout error:', error);
  }
  localStorage.clear();
  
  // Clear browser history and prevent back button access
  window.history.replaceState(null, '', '/login.html');
  window.location.replace('/login.html');
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initAuthentication();
}); 