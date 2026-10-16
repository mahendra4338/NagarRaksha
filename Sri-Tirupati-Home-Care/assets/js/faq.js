/* =====================================================================
   FAQ.JS — Live search + category tab filtering for the FAQ accordion
   ===================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  const searchInput = document.getElementById('faqSearchInput');
  const categoryBtns = document.querySelectorAll('.faq-category-tabs button');
  const faqItems = document.querySelectorAll('.faq-accordion .accordion-item');
  const noResults = document.querySelector('.faq-no-results');

  let activeCategory = 'all';

  function applyFilters() {
    const term = (searchInput ? searchInput.value : '').trim().toLowerCase();
    let visibleCount = 0;

    faqItems.forEach(function (item) {
      const category = item.getAttribute('data-category');
      const text = item.textContent.toLowerCase();
      const matchesCategory = activeCategory === 'all' || category === activeCategory;
      const matchesSearch = term === '' || text.includes(term);

      if (matchesCategory && matchesSearch) {
        item.style.display = '';
        visibleCount++;
      } else {
        item.style.display = 'none';
      }
    });

    if (noResults) noResults.classList.toggle('show', visibleCount === 0);
  }

  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }

  categoryBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      categoryBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-category');
      applyFilters();
    });
  });

});
