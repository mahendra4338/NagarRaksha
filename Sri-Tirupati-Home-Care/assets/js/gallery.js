/* =====================================================================
   GALLERY.JS — Category filtering + custom lightbox viewer
   ===================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  const filterBtns = document.querySelectorAll('.gallery-filter-btn');
  const items = document.querySelectorAll('.gallery-item');

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');

      items.forEach(function (item) {
        const cat = item.getAttribute('data-category');
        if (filter === 'all' || cat === filter) {
          item.classList.remove('hide');
        } else {
          item.classList.add('hide');
        }
      });
    });
  });

  /* ---------- Lightbox ---------- */
  const lightbox = document.getElementById('stcLightbox');
  if (!lightbox) return;
  const lightboxImg = lightbox.querySelector('img');
  const closeBtn = lightbox.querySelector('.stc-lightbox-close');
  const prevBtn = lightbox.querySelector('.stc-lightbox-nav.prev');
  const nextBtn = lightbox.querySelector('.stc-lightbox-nav.next');
  let visibleItems = [];
  let currentIndex = 0;

  function openLightbox(index) {
    visibleItems = Array.from(items).filter(function (i) { return !i.classList.contains('hide'); });
    currentIndex = visibleItems.indexOf(index);
    updateLightboxImage();
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function updateLightboxImage() {
    const img = visibleItems[currentIndex].querySelector('img');
    lightboxImg.src = img.src;
    lightboxImg.alt = img.alt;
  }

  items.forEach(function (item) {
    item.addEventListener('click', function () { openLightbox(item); });
  });

  if (closeBtn) closeBtn.addEventListener('click', function () {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
  });

  if (nextBtn) nextBtn.addEventListener('click', function () {
    currentIndex = (currentIndex + 1) % visibleItems.length;
    updateLightboxImage();
  });

  if (prevBtn) prevBtn.addEventListener('click', function () {
    currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
    updateLightboxImage();
  });

  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    }
  });

  document.addEventListener('keydown', function (e) {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') closeBtn.click();
    if (e.key === 'ArrowRight') nextBtn.click();
    if (e.key === 'ArrowLeft') prevBtn.click();
  });

});
