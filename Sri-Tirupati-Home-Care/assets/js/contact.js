/* =====================================================================
   CONTACT.JS — Instant client-side validation for the contact form
   Note: this demo has no backend; hook the fetch() call up to your
   own form-handling endpoint (e.g. Formspree, EmailJS, or a server route).
   ===================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  const form = document.getElementById('stcContactForm');
  if (!form) return;
  const msgBox = document.getElementById('stcFormMsg');

  function showMessage(type, text) {
    msgBox.textContent = text;
    msgBox.className = 'form-msg ' + type;
  }

  function validateField(field) {
    const value = field.value.trim();
    let valid = true;

    if (field.hasAttribute('required') && value === '') valid = false;
    if (field.type === 'email' && value !== '') {
      valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }
    if (field.type === 'tel' && value !== '') {
      valid = /^[0-9+\-\s()]{10,15}$/.test(value);
    }

    field.classList.toggle('is-invalid', !valid);
    field.classList.toggle('is-valid', valid && value !== '');
    return valid;
  }

  form.querySelectorAll('input, textarea, select').forEach(function (field) {
    field.addEventListener('blur', function () { validateField(field); });
    field.addEventListener('input', function () {
      if (field.classList.contains('is-invalid')) validateField(field);
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    let allValid = true;
    form.querySelectorAll('input, textarea, select').forEach(function (field) {
      if (!validateField(field)) allValid = false;
    });

    if (!allValid) {
      showMessage('error', 'Please check the highlighted fields and try again.');
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Sending…';

    /* Simulated submission — replace with a real endpoint call */
    setTimeout(function () {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
      showMessage('success', 'Thank you! Your message has been received — our care team will call you back shortly.');
      form.reset();
      form.querySelectorAll('.is-valid').forEach(function (f) { f.classList.remove('is-valid'); });
    }, 900);
  });

});
