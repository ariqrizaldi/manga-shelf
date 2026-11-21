(function () {
  "use strict";

  var csrfMeta = document.querySelector('meta[name="csrf-token"]');

  if (csrfMeta) {
    document.body.addEventListener("htmx:configRequest", function (evt) {
      evt.detail.headers["X-CSRF-Token"] = csrfMeta.content;
    });
  }

  var timerToast = null;

  function tampilkanToast(teks) {
    var el = document.getElementById("toast");
    if (!el || !teks) return;
    if (timerToast) clearTimeout(timerToast);
    el.textContent = teks;
    el.hidden = false;
    timerToast = setTimeout(function () {
      el.hidden = true;
    }, 3000);
  }

  window.tampilkanToast = tampilkanToast;

  document.body.addEventListener("showToast", function (evt) {
    var detail = evt.detail || {};
    tampilkanToast(detail.text || detail.value || "");
  });

  document.body.addEventListener("htmx:responseError", function () {
    tampilkanToast("Permintaan gagal. Coba lagi.");
  });

  function salinFallback(teks) {
    var area = document.createElement("textarea");
    area.value = teks;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.top = "-1000px";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (err) {
      ok = false;
    }
    area.remove();
    return ok;
  }

  function salinTeks(btn) {
    var teks = btn.getAttribute("data-copy") || "";
    if (!teks) {
      var target = btn.getAttribute("data-copy-target");
      var el = target ? document.querySelector(target) : null;
      if (el) teks = "value" in el ? el.value : el.textContent;
    }
    if (!teks) return;

    var selesai = function (ok) {
      var labelAwal = btn.textContent;
      btn.textContent = ok ? "Tersalin" : "Gagal menyalin";
      setTimeout(function () {
        btn.textContent = labelAwal;
      }, 1500);
      if (ok) tampilkanToast("Disalin ke papan klip.");
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(teks).then(
        function () {
          selesai(true);
        },
        function () {
          selesai(salinFallback(teks));
        }
      );
    } else {
      selesai(salinFallback(teks));
    }
  }

  window.salinTeks = salinTeks;

  document.querySelectorAll("dialog").forEach(function (dialog) {
    dialog.addEventListener("click", function (evt) {
      if (evt.target === dialog) dialog.close();
    });
  });

  if (window.__toastAwal) {
    tampilkanToast(window.__toastAwal);
  }
})();
