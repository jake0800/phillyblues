(function () {
  'use strict';
  function track(name, params) {
    // Never send form values, personal identifiers, or server error messages to GA.
    try { if (typeof window.gtag === 'function') window.gtag('event', name, params); } catch (_) {}
  }
  var menu = document.getElementById('site-navigation');
  var toggle = document.getElementById('mobile-menu-toggle');
  function closeMenu() { menu.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); }
  if (menu && toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open)); menu.classList.toggle('is-open', open);
    });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); }
    });
    window.matchMedia('(max-width:820px)').addEventListener('change', closeMenu);
  }
  var form = document.getElementById('join-form');
  if (!form) return;
  var submit = form.querySelector('[type=submit]');
  var status = document.getElementById('signup-status');
  var memberFields = document.getElementById('membership-fields');
  var firstName = document.getElementById('fname');
  var consent = document.getElementById('newsletter');
  var intentInputs = form.querySelectorAll('[name=signup_type]');
  var busy = false, accepted = false;
  var started = {};
  function kind() { return form.querySelector('[name=signup_type]:checked').value; }
  function configure() {
    var membership = kind() === 'membership';
    memberFields.hidden = !membership;
    memberFields.querySelectorAll('input,textarea').forEach(function (input) { input.disabled = !membership; });
    firstName.required = membership;
    document.getElementById('first-name-optional').hidden = membership;
    document.getElementById('lname').required = membership;
    consent.required = !membership;
    submit.textContent = membership ? 'Request membership information' : 'Send my signup request';
  }
  intentInputs.forEach(function (input) { input.addEventListener('change', configure); });
  document.querySelectorAll('[data-signup-type]').forEach(function (link) {
    link.addEventListener('click', function () {
      if (!busy && !accepted) {
        intentInputs.forEach(function (input) { input.checked = input.value === link.dataset.signupType; });
        configure();
      }
      track('signup_open', { signup_type: link.dataset.signupType, placement: link.dataset.placement || 'page' });
    });
  });
  document.querySelectorAll('a[href*="google.com/maps"]').forEach(function (link) {
    link.addEventListener('click', function () { track('directions_click', { placement: link.dataset.placement || 'venue' }); });
  });
  form.addEventListener('input', function (e) {
    if (e.target.name === 'signup_type') return;
    var type = kind();
    if (!started[type]) { started[type] = true; track('signup_start', { signup_type: type, form_id: 'join-form' }); }
  });
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (busy || accepted || !form.reportValidity()) return;
    var type = kind();
    var body = new FormData(form);
    busy = true; submit.disabled = true; submit.textContent = 'Sending…';
    intentInputs.forEach(function (input) { input.disabled = true; });
    form.setAttribute('aria-busy', 'true'); status.hidden = false; status.classList.remove('is-error'); status.textContent = 'Sending your request…';
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 20000);
    try {
      var response = await fetch(form.action, { method: 'POST', body: body, headers: { Accept: 'application/json' }, signal: controller.signal });
      var result = await response.json();
      if (!response.ok || result.errors || result.ok === false) {
        var error = new Error('rejected'); error.rejected = true; throw error;
      }
      accepted = true;
      track('generate_lead', { signup_type: type, form_id: 'join-form' });
      form.hidden = true;
      status.textContent = type === 'membership'
        ? 'Request received. Thanks for getting in touch! The Philly Blues will follow up with membership information.'
        : 'Request received. Thanks for getting in touch! We’ve received your request for matchday emails.';
      status.focus();
    } catch (error) {
      status.classList.add('is-error');
      status.textContent = error.rejected
        ? 'Your request wasn’t accepted. Please check your details and try again, or email phillyblues2010@gmail.com.'
        : 'We couldn’t confirm whether your request arrived. Your details are still here. Please contact phillyblues2010@gmail.com before trying again if you’re unsure.';
      track('signup_error', { signup_type: type, error_type: error.rejected ? 'rejected' : 'connection', form_id: 'join-form' });
      status.focus();
    } finally {
      clearTimeout(timeout); busy = false; form.removeAttribute('aria-busy');
      if (!accepted) { submit.disabled = false; intentInputs.forEach(function (input) { input.disabled = false; }); configure(); }
    }
  });
  configure();
})();
