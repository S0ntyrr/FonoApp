document.addEventListener("DOMContentLoaded", function () {
    const splash = document.getElementById("splash");
    const btnHamb = document.getElementById("btn-hamburguesa");
    const panel = document.getElementById("panelPerfil");
    const overlay = document.getElementById("overlay");
    const lista = document.getElementById("listaActividades");
    const btnComenzar = document.getElementById("btnComenzar");

    // Mostrar splash por breve tiempo
    if (splash) {
        setTimeout(() => {
            splash.style.display = "none";
        }, 1400);
    }

    function abrirPanel() {
        panel.classList.add("abierto");
        overlay.classList.add("visible");
    }

    function cerrarPanel() {
        panel.classList.remove("abierto");
        overlay.classList.remove("visible");
    }

    if (btnHamb) btnHamb.addEventListener("click", abrirPanel);
    if (overlay) overlay.addEventListener("click", cerrarPanel);

    // Selección de actividad (lista)
    if (lista) {
        lista.addEventListener("click", (ev) => {
            let item = ev.target;
            // Subir hasta el elemento actividad-item si hace falta
            while (item && !item.classList.contains("actividad-item")) {
                item = item.parentElement;
            }
            if (!item) return;

            // Deseleccionar otros
            document.querySelectorAll(".actividad-item.selected").forEach((it) => {
                it.classList.remove("selected");
            });

            // Seleccionar actual
            item.classList.add("selected");
            const actividad = item.getAttribute("data-actividad");
            btnComenzar.disabled = false;
            btnComenzar.dataset.actividad = actividad || "";
        });
    }

    if (btnComenzar) {
        btnComenzar.addEventListener("click", () => {
            const act = btnComenzar.dataset.actividad;
            if (!act) return;
            // Redirigir a una ruta que manejará el inicio de la actividad (puede implementarse luego)
            const url = `/paciente/comenzar?actividad=${encodeURIComponent(act)}`;
            window.location.href = url;
        });
    }
});
