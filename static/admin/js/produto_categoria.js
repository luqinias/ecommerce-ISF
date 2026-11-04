/* Admin de produto: ao escolher a categoria principal num produto novo, recarrega a página
   para mostrar os campos da ficha técnica daquela categoria. */
(function () {
  "use strict";
  function iniciar($) {
    const adicionando = /\/add\/?$/.test(window.location.pathname);
    $(document).on("change", "#id_primary_category", function () {
      const valor = $(this).val();
      if (!valor) return;
      if (adicionando) {
        const url = new URL(window.location.href);
        url.searchParams.set("primary_category", valor);
        window.location.href = url.toString();
      } else if (!document.getElementById("aviso-ficha")) {
        const aviso = document.createElement("p");
        aviso.id = "aviso-ficha";
        aviso.className = "help";
        aviso.textContent = "Categoria alterada: use \"Salvar e continuar editando\" para atualizar os campos da ficha técnica.";
        this.closest(".form-row, .form-group, div").appendChild(aviso);
      }
    });
  }
  if (window.django && window.django.jQuery) iniciar(window.django.jQuery);
  else document.addEventListener("DOMContentLoaded", () => window.django && iniciar(window.django.jQuery));
})();
