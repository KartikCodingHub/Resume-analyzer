(function () {
  function getElement(selector) {
    return document.querySelector(selector);
  }
  function getElements(selector) {
    return Array.from(document.querySelectorAll(selector));
  }

  function setYear() {
    var yearEl = getElement('#year');
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  }

  function setupMobileNav() {
    var headerInner = getElement('.header-inner');
    var toggle = getElement('#nav-toggle');
    var nav = getElement('#site-nav');
    if (!headerInner || !toggle || !nav) return;

    function closeNav() {
      headerInner.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }

    function openNav() {
      headerInner.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
    }

    toggle.addEventListener('click', function () {
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      if (expanded) {
        closeNav();
      } else {
        openNav();
      }
    });

    // Close on link click (mobile)
    getElements('#site-nav a').forEach(function (link) {
      link.addEventListener('click', function () {
        closeNav();
      });
    });
  }

  function setupSmoothScroll() {
    getElements('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener('click', function (e) {
        var href = anchor.getAttribute('href');
        if (!href || href.length <= 1) return;
        var id = href.slice(1);
        var target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          target.focus({ preventScroll: true });
        }
      });
    });
  }

  function applyTheme(theme) {
    var html = document.documentElement;
    if (theme === 'light' || theme === 'dark') {
      html.setAttribute('data-theme', theme);
    } else {
      html.setAttribute('data-theme', 'auto');
    }
    var icon = getElement('#theme-toggle .theme-icon');
    if (icon) {
      icon.setAttribute('data-mode', theme || 'auto');
      icon.textContent = theme === 'dark' ? '🌙' : theme === 'light' ? '☀️' : '🌓';
    }
  }

  function setupThemeToggle() {
    var toggle = getElement('#theme-toggle');
    if (!toggle) return;

    var stored = localStorage.getItem('theme');
    applyTheme(stored || 'auto');
    toggle.setAttribute('aria-pressed', stored === 'dark' || stored === 'light' ? 'true' : 'false');

    toggle.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      var next = current === 'auto' ? 'dark' : current === 'dark' ? 'light' : 'auto';
      if (next === 'auto') localStorage.removeItem('theme'); else localStorage.setItem('theme', next);
      toggle.setAttribute('aria-pressed', next === 'dark' || next === 'light' ? 'true' : 'false');
      applyTheme(next);
    });
  }

  function setupFormHandling() {
    var form = getElement('#contact-form');
    var status = getElement('#form-status');
    if (!form || !status) return;

    function setStatus(message, type) {
      status.textContent = message;
      status.style.color = type === 'error' ? '#ef4444' : '';
    }

    function validate(formData) {
      var errors = {};
      var name = String(formData.get('name') || '').trim();
      var email = String(formData.get('email') || '').trim();
      var message = String(formData.get('message') || '').trim();
      var consent = form.querySelector('#consent');

      if (!name) errors.name = 'Please enter your name.';
      if (!email) errors.email = 'Please enter your email.';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'Please enter a valid email.';
      if (!message) errors.message = 'Please enter a message.';
      if (!(consent && consent.checked)) errors.consent = 'Please accept the consent.';
      return errors;
    }

    function setFieldMessage(field, message) {
      var el = getElement('.field-msg[data-field="' + field + '"]');
      if (el) el.textContent = message || '';
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      setStatus('', '');
      ['name', 'email', 'message'].forEach(function (f) { setFieldMessage(f, ''); });

      var formData = new FormData(form);
      var errors = validate(formData);
      if (Object.keys(errors).length) {
        if (errors.name) setFieldMessage('name', errors.name);
        if (errors.email) setFieldMessage('email', errors.email);
        if (errors.message) setFieldMessage('message', errors.message);
        if (errors.consent) setStatus(errors.consent, 'error');
        return;
      }

      var button = form.querySelector('button[type="submit"]');
      if (button) button.disabled = true;
      setStatus('Sending…', '');

      // Simulate async submission
      setTimeout(function () {
        setStatus('Thanks! We will get back to you shortly.', '');
        form.reset();
        if (button) button.disabled = false;
      }, 800);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setYear();
    setupMobileNav();
    setupSmoothScroll();
    setupThemeToggle();
    setupFormHandling();
  });
})();