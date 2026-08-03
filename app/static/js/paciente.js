document.addEventListener("DOMContentLoaded", function () {
    const btnHamb = document.getElementById("btn-hamburguesa");
    const btnCerrar = document.getElementById("btn-cerrar-panel");
    const panel = document.getElementById("panelPerfil");
    const overlay = document.getElementById("overlay");

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

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") cerrarPanel();
    });
});
