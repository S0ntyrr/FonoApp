document.addEventListener("DOMContentLoaded", function () {
    const splash = document.getElementById("splash");
    const btnHamb = document.getElementById("btn-hamburguesa");
    const btnCerrar = document.getElementById("btn-cerrar-panel");
    const panel = document.getElementById("panelPerfil");
    const overlay = document.getElementById("overlay");
    const lista = document.getElementById("listaActividades");
    const btnComenzar = document.getElementById("btnComenzar");

    if (splash) {
        setTimeout(() => {
            splash.style.transition = "opacity 0.5s ease";
            splash.style.opacity = "0";
            setTimeout(() => { splash.style.display = "none"; }, 500);
        }, 1800);
    }

    function abrirPanel() {
        if (panel) panel.classList.add("abierto");
        if (overlay) overlay.classList.add("visible");
        document.body.style.overflow = "hidden";
    }
    function cerrarPanel() {
        if (panel) panel.classList.remove("abierto");
        if (overlay) overlay.classList.remove("visible");
        document.body.style.overflow = "";
    }

    if (btnHamb) btnHamb.addEventListener("click", abrirPanel);
    if (btnCerrar) btnCerrar.addEventListener("click", cerrarPanel);
    if (overlay) overlay.addEventListener("click", cerrarPanel);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") cerrarPanel(); });

    if (lista) {
        lista.addEventListener("click", (ev) => {
            let item = ev.target;
            while (item && !item.classList.contains("actividad-item")) item = item.parentElement;
            if (!item) return;
            document.querySelectorAll(".actividad-item.selected").forEach(it => it.classList.remove("selected"));
            item.classList.add("selected");
            if (btnComenzar) {
                btnComenzar.disabled = false;
                btnComenzar.dataset.actividad = item.getAttribute("data-actividad") || "";
            }
        });
    }

    if (btnComenzar) {
        btnComenzar.addEventListener("click", () => {
            if (!btnComenzar.dataset.actividad) return;
            window.location.href = "/juegos/";
        });
    }
});
