/* Comportamentos do site em JS puro (progressivo: sem JS, links e formulários continuam funcionando).
   Módulos: dropdowns, menu mobile, busca mobile, header sticky, rolar para cima, cookies, toasts,
   expansores, galeria, seletor de variação e quantidade. */
(function () {
  "use strict";

  const $ = (sel, raiz = document) => raiz.querySelector(sel);
  const $$ = (sel, raiz = document) => Array.from(raiz.querySelectorAll(sel));
  const hover = window.matchMedia("(hover: hover) and (pointer: fine)");

  /* ---------- Dropdowns (C04, C05, C07) ---------- */
  function fecharDropdowns(exceto) {
    $$("[data-dd]").forEach((dd) => {
      if (dd === exceto) return;
      const g = $("[data-dd-gatilho]", dd);
      const p = $("[data-dd-painel]", dd);
      if (g && p && !p.hidden) {
        g.setAttribute("aria-expanded", "false");
        p.hidden = true;
      }
    });
  }

  function iniciarDropdowns() {
    $$("[data-dd]").forEach((dd) => {
      const gatilho = $("[data-dd-gatilho]", dd);
      const painel = $("[data-dd-painel]", dd);
      if (!gatilho || !painel) return;
      let abertoEm = 0;
      const abrir = () => { fecharDropdowns(dd); painel.hidden = false; gatilho.setAttribute("aria-expanded", "true"); abertoEm = Date.now(); };
      const fechar = () => { painel.hidden = true; gatilho.setAttribute("aria-expanded", "false"); };
      gatilho.addEventListener("click", (e) => {
        e.stopPropagation();
        const aberto = gatilho.getAttribute("aria-expanded") === "true";
        // clique logo depois do hover não fecha o painel que acabou de abrir
        if (aberto && Date.now() - abertoEm < 400) return;
        aberto ? fechar() : abrir();
      });
      if (dd.hasAttribute("data-dd-hover")) {
        let t;
        dd.addEventListener("mouseenter", () => { if (hover.matches) { clearTimeout(t); if (painel.hidden) abrir(); } });
        dd.addEventListener("mouseleave", () => { if (hover.matches) { t = setTimeout(fechar, 180); } });
      }
      dd.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !painel.hidden) { fechar(); gatilho.focus(); }
      });
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest("[data-dd]")) fecharDropdowns();
    });
  }

  /* ---------- Menu mobile (C06) ---------- */
  function iniciarMenuMobile() {
    const menu = $("[data-menu-mobile]");
    const botao = $("[data-menu-abrir]");
    if (!menu || !botao) return;
    let ultimoFoco = null;
    const abrir = () => {
      ultimoFoco = document.activeElement;
      menu.hidden = false;
      requestAnimationFrame(() => menu.classList.add("aberto"));
      document.body.classList.add("trava-rolagem");
      botao.setAttribute("aria-expanded", "true");
      const primeiro = $("[data-menu-fechar].botao-icone", menu);
      if (primeiro) primeiro.focus();
    };
    const fechar = () => {
      menu.classList.remove("aberto");
      document.body.classList.remove("trava-rolagem");
      botao.setAttribute("aria-expanded", "false");
      const duracao = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--t-slow")) || 0;
      setTimeout(() => { menu.hidden = true; }, duracao);
      if (ultimoFoco) ultimoFoco.focus();
    };
    botao.addEventListener("click", abrir);
    $$("[data-menu-fechar]", menu).forEach((el) => el.addEventListener("click", fechar));
    menu.addEventListener("keydown", (e) => {
      if (e.key === "Escape") fechar();
      if (e.key === "Tab") { // mantém o foco dentro do painel
        const focaveis = $$("a[href], button, summary, input", menu).filter((el) => el.offsetParent !== null);
        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus(); }
        else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus(); }
      }
    });
  }

  /* ---------- Busca (mobile: botão mostra o campo) ---------- */
  function iniciarBusca() {
    const alternar = $("[data-busca-alternar]");
    const form = $("[data-busca]");
    if (alternar && form) {
      alternar.addEventListener("click", () => {
        const aberta = form.classList.toggle("aberta");
        alternar.setAttribute("aria-expanded", String(aberta));
        if (aberta) $("input", form).focus();
      });
    }
    const sugestoes = $("#busca-sugestoes");
    if (sugestoes) {
      document.addEventListener("click", (e) => { if (!e.target.closest("[data-busca]")) sugestoes.innerHTML = ""; });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") sugestoes.innerHTML = ""; });
    }
  }

  /* ---------- Header sticky e rolar para cima (C03, C10) ---------- */
  function iniciarRolagem() {
    const cabecalho = $("[data-cabecalho]");
    const topo = $("[data-rolar-topo]");
    const aoRolar = () => {
      const y = window.scrollY;
      if (cabecalho) cabecalho.classList.toggle("rolado", y > 8);
      if (topo) topo.classList.toggle("visivel", y > 600);
    };
    window.addEventListener("scroll", aoRolar, { passive: true });
    aoRolar();
    if (topo) {
      topo.addEventListener("click", () => {
        const suave = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: suave ? "smooth" : "auto" });
        const alvo = $("#conteudo");
        if (alvo) alvo.focus({ preventScroll: true });
      });
    }
  }

  /* ---------- Cookies e analytics (C09, LGPD) ---------- */
  const COOKIE = "isf_consent";
  function lerConsentimento() {
    const m = document.cookie.match(new RegExp("(?:^|; )" + COOKIE + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }
  function gravarConsentimento(valor) {
    const umAno = 60 * 60 * 24 * 180;
    const seguro = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${COOKIE}=${encodeURIComponent(valor)}; Max-Age=${umAno}; Path=/; SameSite=Lax${seguro}`;
  }
  function iniciarCookies() {
    const banner = $("[data-cookies]");
    if (!banner) return;
    const escolha = lerConsentimento();
    banner.hidden = Boolean(escolha);
    if (escolha === "todos") document.dispatchEvent(new CustomEvent("isf:consentimento", { detail: "todos" }));
    $$("[data-cookies-escolha]", banner).forEach((b) => b.addEventListener("click", () => {
      const valor = b.getAttribute("data-cookies-escolha");
      const anterior = lerConsentimento();
      gravarConsentimento(valor);
      banner.hidden = true;
      if (valor === "todos") document.dispatchEvent(new CustomEvent("isf:consentimento", { detail: "todos" }));
      else if (anterior === "todos") location.reload(); // revoga: recarrega sem os rastreadores
    }));
    $$("[data-cookies-abrir]").forEach((b) => b.addEventListener("click", () => {
      banner.hidden = false;
      const primeiro = $("button", banner);
      if (primeiro) primeiro.focus();
    }));
  }

  /* ---------- Toasts (disparados pelo servidor via HX-Trigger: {"isf:toast": {...}}) ---------- */
  function mostrarToast({ mensagem, link, rotulo, tipo }) {
    const area = $("#toasts");
    if (!area || !mensagem) return;
    const el = document.createElement("div");
    el.className = "toast" + (tipo === "erro" ? " toast--erro" : "");
    el.setAttribute("role", "status");
    const texto = document.createElement("span");
    texto.textContent = mensagem;
    el.appendChild(texto);
    if (link) {
      const a = document.createElement("a");
      a.href = link;
      a.textContent = rotulo || "Ver";
      el.appendChild(a);
    }
    area.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  }
  document.addEventListener("isf:toast", (e) => mostrarToast(e.detail || {}));
  window.isfToast = mostrarToast;

  /* ---------- Expansores genéricos (descrição, portfólio) ---------- */
  function iniciarExpansores(raiz = document) {
    $$("[data-expandir]", raiz).forEach((botao) => {
      if (botao.dataset.pronto) return;
      botao.dataset.pronto = "1";
      const alvo = document.getElementById(botao.getAttribute("aria-controls"));
      if (!alvo) return;
      const textoMais = botao.dataset.textoMais || botao.textContent.trim();
      const textoMenos = botao.dataset.textoMenos || textoMais;
      botao.addEventListener("click", () => {
        const aberto = botao.getAttribute("aria-expanded") === "true";
        botao.setAttribute("aria-expanded", String(!aberto));
        alvo.classList.toggle("expandido", !aberto);
        const rotulo = $("[data-rotulo]", botao) || botao;
        rotulo.textContent = aberto ? textoMais : textoMenos;
      });
    });
  }

  /* ---------- Auto-submit (ordenação) ---------- */
  function iniciarAutoSubmit(raiz = document) {
    $$("[data-auto-submit]", raiz).forEach((campo) => {
      campo.addEventListener("change", () => campo.form && campo.form.requestSubmit());
    });
  }

  /* ---------- Quantidade (stepper com mínimo e múltiplo) ---------- */
  function ajustarQuantidade(input, valor) {
    const min = parseInt(input.min || "1", 10);
    const passo = parseInt(input.step || "1", 10) || 1;
    let v = Number.isFinite(valor) ? valor : min;
    if (v < min) v = min;
    // arredonda para o múltiplo do passo a partir do mínimo
    v = min + Math.round((v - min) / passo) * passo;
    input.value = v;
    const caixa = input.closest("[data-quantidade]");
    if (caixa) {
      const menos = $("[data-qtd-menos]", caixa);
      if (menos) menos.disabled = v <= min;
    }
    input.dispatchEvent(new Event("input", { bubbles: true }));
    return v;
  }
  function iniciarQuantidades(raiz = document) {
    $$("[data-quantidade]", raiz).forEach((caixa) => {
      if (caixa.dataset.pronto) return;
      caixa.dataset.pronto = "1";
      const input = $("input", caixa);
      const passo = () => parseInt(input.step || "1", 10) || 1;
      const mais = $("[data-qtd-mais]", caixa);
      const menos = $("[data-qtd-menos]", caixa);
      if (mais) mais.addEventListener("click", () => { ajustarQuantidade(input, parseInt(input.value, 10) + passo()); input.dispatchEvent(new Event("change", { bubbles: true })); });
      if (menos) menos.addEventListener("click", () => { ajustarQuantidade(input, parseInt(input.value, 10) - passo()); input.dispatchEvent(new Event("change", { bubbles: true })); });
      input.addEventListener("blur", () => ajustarQuantidade(input, parseInt(input.value, 10)));
      ajustarQuantidade(input, parseInt(input.value, 10));
    });
  }

  /* ---------- Galeria do produto (P01) ---------- */
  function iniciarGalerias(raiz = document) {
    $$("[data-galeria]", raiz).forEach((gal) => {
      if (gal.dataset.pronto) return;
      gal.dataset.pronto = "1";
      const principal = $("[data-galeria-principal]", gal);
      const miniaturas = $$("[data-galeria-mini]", gal);
      const dialogo = $("[data-galeria-dialogo]", gal);
      let atual = 0;
      const mostrar = (i) => {
        if (!miniaturas.length) return;
        atual = (i + miniaturas.length) % miniaturas.length;
        const m = miniaturas[atual];
        principal.src = m.dataset.src;
        if (m.dataset.srcset) principal.srcset = m.dataset.srcset;
        principal.alt = m.dataset.alt || "";
        miniaturas.forEach((x, j) => x.setAttribute("aria-current", j === atual ? "true" : "false"));
      };
      miniaturas.forEach((m, i) => m.addEventListener("click", () => mostrar(i)));
      $$("[data-galeria-anterior]", gal).forEach((b) => b.addEventListener("click", () => mostrar(atual - 1)));
      $$("[data-galeria-proxima]", gal).forEach((b) => b.addEventListener("click", () => mostrar(atual + 1)));
      gal.addEventListener("isf:galeria-ir", (e) => {
        const i = miniaturas.findIndex((m) => m.dataset.imagemId === String(e.detail));
        if (i >= 0) mostrar(i);
      });
      if (dialogo && typeof dialogo.showModal === "function") {
        const imgGrande = $("img", dialogo);
        $$("[data-galeria-ampliar]", gal).forEach((b) => b.addEventListener("click", () => {
          const m = miniaturas[atual];
          imgGrande.src = (m && m.dataset.grande) || principal.src;
          imgGrande.alt = principal.alt;
          dialogo.showModal();
        }));
        $$("[data-galeria-fechar]", dialogo).forEach((b) => b.addEventListener("click", () => dialogo.close()));
        dialogo.addEventListener("click", (e) => { if (e.target === dialogo) dialogo.close(); });
      }
    });
  }

  /* ---------- Seletor de variação (P03 + P05) ---------- */
  function iniciarSeletores(raiz = document) {
    $$("[data-seletor-variacao]", raiz).forEach((form) => {
      if (form.dataset.pronto) return;
      form.dataset.pronto = "1";
      const variacoes = JSON.parse(form.dataset.variacoes || "[]");
      const grupos = $$("[data-atributo]", form);
      const botao = $("[data-adicionar]", form);
      const aviso = $("[data-aviso-variacao]", form);
      const campoVariacao = $("input[name=variant]", form);
      const skuAlvo = document.querySelector("[data-sku]");
      const skuPadrao = skuAlvo ? skuAlvo.textContent : "";
      const barra = document.querySelector("[data-barra-fixa]");

      const escolhidos = () => {
        const sel = {};
        grupos.forEach((g) => {
          const marcado = $("input:checked", g);
          if (marcado) sel[g.dataset.atributo] = marcado.value;
        });
        return sel;
      };
      const encontrar = (sel) => variacoes.find((v) => Object.keys(v.atributos).every((k) => String(v.atributos[k]) === String(sel[k])));
      const disponivel = (chave, valor, sel) => variacoes.some((v) => String(v.atributos[chave]) === String(valor)
        && Object.keys(sel).every((k) => k === chave || String(v.atributos[k]) === String(sel[k])));

      const atualizar = () => {
        const sel = escolhidos();
        // desabilita combinações inexistentes
        grupos.forEach((g) => $$("input", g).forEach((inp) => {
          const ok = disponivel(g.dataset.atributo, inp.value, sel);
          inp.disabled = !ok && !inp.checked;
          inp.closest("label").classList.toggle("indisponivel", !ok);
        }));
        grupos.forEach((g) => {
          const marcado = $("input:checked", g);
          const rotulo = $("[data-valor-escolhido]", g);
          if (rotulo) rotulo.textContent = marcado ? marcado.dataset.rotulo : rotulo.dataset.vazio;
        });
        const completo = grupos.every((g) => $("input:checked", g));
        const variacao = completo ? encontrar(sel) : null;
        if (campoVariacao) campoVariacao.value = variacao ? variacao.id : "";
        const liberado = Boolean(variacao) || grupos.length === 0;
        if (botao) {
          botao.setAttribute("aria-disabled", String(!liberado));
          botao.classList.toggle("bloqueado", !liberado);
        }
        if (liberado && aviso) aviso.hidden = true;
        if (skuAlvo) skuAlvo.textContent = variacao ? variacao.sku : skuPadrao;
        if (variacao && variacao.imagem) {
          const gal = document.querySelector("[data-galeria]");
          if (gal) gal.dispatchEvent(new CustomEvent("isf:galeria-ir", { detail: variacao.imagem }));
        }
        if (barra) {
          const msg = $("[data-barra-msg]", barra);
          if (msg) msg.textContent = liberado ? "Pronto para adicionar" : msg.dataset.vazio;
        }
        form.dispatchEvent(new CustomEvent("isf:variacao", { detail: variacao, bubbles: true }));
      };

      grupos.forEach((g) => $$("input", g).forEach((inp) => inp.addEventListener("change", atualizar)));
      const limpar = $("[data-limpar-variacao]", form);
      if (limpar) limpar.addEventListener("click", () => { $$("input[type=radio]", form).forEach((i) => { i.checked = false; }); atualizar(); });

      // bloqueio: impede o envio (com ou sem HTMX) até escolher a variação
      const bloquear = (e) => {
        if (botao && botao.getAttribute("aria-disabled") === "true") {
          e.preventDefault();
          e.stopImmediatePropagation();
          if (aviso) { aviso.hidden = false; aviso.focus && aviso.focus(); }
          const primeiro = $("[data-atributo] input:not(:checked)", form);
          if (primeiro) primeiro.closest("[data-atributo]").scrollIntoView({ block: "center", behavior: "smooth" });
          return false;
        }
        return true;
      };
      form.addEventListener("submit", bloquear, true);
      form.addEventListener("htmx:confirm", (e) => { if (!bloquear(e)) e.preventDefault(); });
      if (barra) {
        const b = $("button", barra);
        if (b) b.addEventListener("click", () => {
          if (botao && botao.getAttribute("aria-disabled") === "true") {
            const g = $("[data-atributo]", form);
            if (g) g.scrollIntoView({ block: "center", behavior: "smooth" });
            if (aviso) aviso.hidden = false;
          } else if (botao) botao.click();
        });
      }
      atualizar();
    });
  }

  /* ---------- Ligações ---------- */
  function iniciarTudo(raiz) {
    iniciarExpansores(raiz);
    iniciarAutoSubmit(raiz);
    iniciarQuantidades(raiz);
    iniciarGalerias(raiz);
    iniciarSeletores(raiz);
  }

  document.addEventListener("DOMContentLoaded", () => {
    iniciarDropdowns();
    iniciarMenuMobile();
    iniciarBusca();
    iniciarRolagem();
    iniciarCookies();
    iniciarTudo(document);
  });
  document.addEventListener("htmx:afterSwap", (e) => iniciarTudo(e.target));
  document.addEventListener("htmx:responseError", () => mostrarToast({ mensagem: "Não foi possível concluir. Tente de novo.", tipo: "erro" }));
})();
