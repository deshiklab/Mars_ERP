// REM ERP — PWA shortcut on the ERPNext login page (injected via web_include_js).
// Adds a "Open REM ERP PWA" link below the login card, scoped to /login only.
(function () {
  if (window.location.pathname !== "/login") return;
  function addPwaLink() {
    var card = document.querySelector(".login-content") ||
               document.querySelector(".login-card") ||
               document.querySelector("#login-card") ||
               document.querySelector("form") ||
               document.querySelector(".page-card");
    if (!card) return;
    if (document.getElementById("rem-pwa-link")) return; // already added
    var wrap = document.createElement("div");
    wrap.id = "rem-pwa-link";
    wrap.style.cssText = "text-align:center;margin-top:14px;padding-top:12px;border-top:1px solid #e8e8e8";
    var a = document.createElement("a");
    a.href = "/assets/mars_constech/rem/index.html";
    a.style.cssText = "display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;color:#2f80ed;text-decoration:none;padding:8px 18px;border:1px solid #d0d8e8;border-radius:8px;background:#f5f8ff";
    a.innerHTML = "<span style='font-size:14px'>🏗️</span> Open REM ERP PWA";
    a.title = "Launch the REM ERP PWA (secure sign-in)";
    wrap.appendChild(a);
    card.appendChild(wrap);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addPwaLink);
  } else {
    addPwaLink();
  }
  // retry for SPA re-renders / slow login page
  setTimeout(addPwaLink, 800);
  setTimeout(addPwaLink, 2500);
})();
