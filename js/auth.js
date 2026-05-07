/* ═══════════════════════════════════════════════════════
   Auth — Firebase Google Sign-In + email allow-list
   Shared by hub (root index.html) + per-product standalones.

   Detects mode automatically:
   - If #loginOverlay exists → "hub" mode (full overlay UI)
   - Otherwise → "standalone" mode (assume hub did the auth;
     replace body with redirect message if not signed in).

   Firebase project is shared with the Cases dashboard
   (cases-tracker-dc2f2) — same allow-list, same OAuth flow.
   ═══════════════════════════════════════════════════════ */

(function() {
  'use strict';

  var FIREBASE_CONFIG = {
    apiKey: "AIzaSyDDuBOndDZ7BXmMDY8AqzLoSNBf2r4rseU",
    authDomain: "cases-tracker-dc2f2.firebaseapp.com",
    databaseURL: "https://cases-tracker-dc2f2-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "cases-tracker-dc2f2",
    storageBucket: "cases-tracker-dc2f2.firebasestorage.app",
    messagingSenderId: "694983914978",
    appId: "1:694983914978:web:6ca811e7bfc31a0487b5bb"
  };

  var ALLOWED_EMAILS = [
    'tom@themothership.ai', 'tom.mickiewicz@themothership.ai',
    'vitali@themothership.ai', 'vitalii.suvorov@themothership.ai',
    'natasha@themothership.ai', 'natasha.heneghan@themothership.ai',
    'leticia@themothership.ai', 'leticia.rivero@themothership.ai',
    'francesco@themothership.ai', 'francesco.diana@themothership.ai',
    'hello@themothership.ai', 'amazon@themothership.ai',
    'arush.pathak@themothership.ai'
  ];

  // Hide page until auth resolved (prevents flash of un-authed content)
  document.documentElement.style.visibility = 'hidden';

  if (typeof firebase === 'undefined') {
    console.error('Firebase SDK not loaded — auth disabled.');
    document.documentElement.style.visibility = 'visible';
    return;
  }

  firebase.initializeApp(FIREBASE_CONFIG);
  var auth = firebase.auth();

  function isHub() {
    return !!document.getElementById('loginOverlay');
  }

  function isAllowed(user) {
    return user && ALLOWED_EMAILS.indexOf(user.email) !== -1;
  }

  function setupHubButtons() {
    var btnIn = document.getElementById('btnSignIn');
    if (btnIn) btnIn.onclick = function() {
      auth.signInWithPopup(new firebase.auth.GoogleAuthProvider())
        .catch(function(err) { console.error('Sign-in error:', err); });
    };
    var btnOut = document.getElementById('btnSignOut');
    if (btnOut) btnOut.onclick = function() { auth.signOut(); };
    var btnOut2 = document.getElementById('btnDeniedSignOut');
    if (btnOut2) btnOut2.onclick = function() { auth.signOut(); };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupHubButtons);
  } else {
    setupHubButtons();
  }

  auth.onAuthStateChanged(function(user) {
    if (isHub()) {
      var overlay = document.getElementById('loginOverlay');
      var bar = document.getElementById('userBar');
      var loginBox = document.getElementById('loginBox');
      var deniedBox = document.getElementById('deniedBox');
      var deniedEmail = document.getElementById('deniedEmail');
      var userName = document.getElementById('userName');
      var userPhoto = document.getElementById('userPhoto');

      if (user) {
        if (!isAllowed(user)) {
          if (loginBox) loginBox.style.display = 'none';
          if (deniedBox) deniedBox.style.display = 'block';
          if (deniedEmail) deniedEmail.textContent = user.email;
          overlay.style.display = 'flex';
          if (bar) bar.style.display = 'none';
          document.documentElement.style.visibility = 'visible';
          return;
        }
        // Allowed
        overlay.style.display = 'none';
        if (loginBox) loginBox.style.display = 'block';
        if (deniedBox) deniedBox.style.display = 'none';
        if (bar) {
          bar.style.display = 'flex';
          if (userName) userName.textContent = user.displayName || user.email;
          if (userPhoto && user.photoURL) userPhoto.src = user.photoURL;
        }
        document.documentElement.style.visibility = 'visible';
      } else {
        // Signed out
        overlay.style.display = 'flex';
        if (loginBox) loginBox.style.display = 'block';
        if (deniedBox) deniedBox.style.display = 'none';
        if (bar) bar.style.display = 'none';
        document.documentElement.style.visibility = 'visible';
      }
    } else {
      // Standalone (in iframe or directly opened)
      if (isAllowed(user)) {
        document.documentElement.style.visibility = 'visible';
      } else {
        document.body.innerHTML =
          '<div style="display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#475569;flex-direction:column;gap:14px;text-align:center;padding:32px;background:#f1f5f9">' +
          '<h2 style="color:#0f2942;margin:0;font-size:1.15rem">Sign in required</h2>' +
          '<p style="margin:0;font-size:.85rem;max-width:360px;line-height:1.5">This dashboard is part of the <a href="../../index.html" target="_top" style="color:#2563eb;font-weight:600;text-decoration:none">Reviews Analysis hub</a>. Please sign in there.</p>' +
          '</div>';
        document.documentElement.style.visibility = 'visible';
      }
    }
  });
})();
