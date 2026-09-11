/* ============================================================
   EdgePeer IX-Fabric — Client-Side Application Logic
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initModals();
  initToasts();
  initFilterTabs();
  initLoadSlider();
  initFormValidation();
});

/* ---------- Mobile Sidebar Toggle ---------- */
function initSidebar() {
  const hamburger = document.getElementById('hamburger-btn');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  if (hamburger && sidebar) {
    hamburger.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (backdrop) backdrop.classList.toggle('open');
    });
  }
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      sidebar.classList.remove('open');
      backdrop.classList.remove('open');
    });
  }
}

/* ---------- Modal Handlers ---------- */
function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-modal-open');
      openModal(id);
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-modal-close');
      closeModal(id);
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        overlay.classList.remove('open');
      }
    });
  });
}

function openModal(id) {
  var el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  var el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

/* ---------- Toast Auto-Dismiss ---------- */
function initToasts() {
  document.querySelectorAll('.toast-banner').forEach(function (toast) {
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-8px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(function () { toast.remove(); }, 300);
    }, 6000);
  });

  document.querySelectorAll('[data-dismiss-toast]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var toast = btn.closest('.toast-banner');
      if (toast) toast.remove();
    });
  });
}

/* ---------- Filter Tabs (Peering Queue) ---------- */
function initFilterTabs() {
  document.querySelectorAll('.filter-tabs').forEach(function (tabGroup) {
    var tabs = tabGroup.querySelectorAll('.filter-tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');

        var filter = tab.getAttribute('data-filter');
        var targetId = tabGroup.getAttribute('data-target');
        var items = document.querySelectorAll(targetId + ' [data-status]');

        items.forEach(function (item) {
          if (filter === 'all' || item.getAttribute('data-status') === filter) {
            item.style.display = '';
          } else {
            item.style.display = 'none';
          }
        });
      });
    });
  });
}

/* ---------- Load Slider ---------- */
function initLoadSlider() {
  var slider = document.getElementById('load-slider');
  var display = document.getElementById('load-display');
  var badge = document.getElementById('load-badge');

  if (slider && display) {
    slider.addEventListener('input', function () {
      var val = parseInt(slider.value);
      display.textContent = val;

      if (badge) {
        if (val < 70) {
          badge.textContent = 'Safe';
          badge.className = 'badge badge--active';
        } else if (val <= 85) {
          badge.textContent = 'Caution';
          badge.className = 'badge badge--pending';
        } else {
          badge.textContent = 'Critical';
          badge.className = 'badge badge--error';
        }
      }
    });
  }
}

/* ---------- Form Validation ---------- */
function initFormValidation() {
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var valid = true;
      form.querySelectorAll('[required]').forEach(function (input) {
        if (!input.value.trim()) {
          input.classList.add('form-input--error');
          valid = false;
        } else {
          input.classList.remove('form-input--error');
        }
      });

      form.querySelectorAll('input[type="number"][min]').forEach(function (input) {
        var val = parseFloat(input.value);
        var min = parseFloat(input.getAttribute('min'));
        if (isNaN(val) || val < min) {
          input.classList.add('form-input--error');
          valid = false;
        } else {
          input.classList.remove('form-input--error');
        }
      });

      if (!valid) {
        e.preventDefault();
      }
    });
  });
}

/* ---------- Button Loading State ---------- */
function setButtonLoading(btn, loading) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.origHtml = btn.innerHTML;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin" style="font-size:16px">refresh</span> Processing...';
  } else {
    btn.disabled = false;
    if (btn.dataset.origHtml) {
      btn.innerHTML = btn.dataset.origHtml;
    }
  }
}
