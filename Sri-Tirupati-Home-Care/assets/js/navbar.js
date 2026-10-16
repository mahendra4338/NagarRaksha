/* =====================================================================
   NAVBAR.JS — Sticky compact header on scroll + mobile menu close on link click
   ===================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  const navbar = document.querySelector('.stc-navbar');

  function handleScroll() {
    if (!navbar) return;
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }
  handleScroll();
  window.addEventListener('scroll', handleScroll);

  /* Close mobile collapse after a nav link is tapped */
  const navCollapse = document.getElementById('stcNavContent');
  if (navCollapse) {
    navCollapse.querySelectorAll('.nav-link, .dropdown-item').forEach(function (link) {
      link.addEventListener('click', function () {
        if (navCollapse.classList.contains('show') && window.bootstrap) {
          const bsCollapse = window.bootstrap.Collapse.getInstance(navCollapse) || new window.bootstrap.Collapse(navCollapse);
          bsCollapse.hide();
        }
      });
    });
  }

});
