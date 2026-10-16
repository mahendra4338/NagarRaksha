/* =====================================================================
   MAIN.JS — Global site behaviour: loader, back-to-top, ripple buttons
   ===================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* ---------- Page loader ---------- */
  const loader = document.getElementById('page-loader');
  if (loader) {
    window.addEventListener('load', function () {
      setTimeout(function () { loader.classList.add('loaded'); }, 300);
    });
  }

  /* ---------- Back to top button ---------- */
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 400) {
        backToTop.classList.add('show');
      } else {
        backToTop.classList.remove('show');
      }
    });
    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- Ripple effect on all .btn elements ---------- */
  document.querySelectorAll('.btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement('span');
      const size = Math.max(rect.width, rect.height);
      ripple.className = 'ripple';
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      btn.appendChild(ripple);
      setTimeout(function () { ripple.remove(); }, 650);
    });
  });

  /* ---------- Current year in footer ---------- */
  document.querySelectorAll('.current-year').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

});
