/**
 * FonoApp - JavaScript del Dashboard del Paciente
 * =================================================
 * Maneja la interactividad del dashboard del paciente:
 *
 * 1. SPLASH SCREEN
 *    - Muestra la pantalla de bienvenida al cargar
 *    - Hace fade-out suave después de 1.8 segundos
 *
 * 2. PANEL DE PERFIL LATERAL
 *    - Se abre al hacer clic en el botón hamburguesa (☰)
 *    - Se cierra con el botón ✕, haciendo clic en el overlay, o con Escape
 *    - Bloquea el scroll del body cuando está abierto
 *
 * 3. SELECCIÓN DE ACTIVIDADES
 *    - Permite seleccionar una actividad de la lista
 *    - Habilita el botón "Comenzar" al seleccionar
 *    - Al hacer clic en "Comenzar", redirige al hub de juegos
 *
 * NOTA: El progreso de actividades completadas se maneja en el template
 *       paciente/perfil.html con localStorage (no en este archivo).
 */

document.addEventListener("DOMContentLoaded", function () {
    // ── Referencias a elementos del DOM ─────────────────────────────────────
    const splash = document.getElementById("splash");
    const btnHamb = document.getElementById("btn-hamburguesa");
    const btnCerrar = document.getElementById("btn-cerrar-panel");
    const panel = document.getElementById("panelPerfil");
    const overlay = document.getElementById("overlay");
    const lista = document.getElementById("listaActividades");
    const btnComenzar = document.getElementById("btnComenzar");

    // ── 1. Splash Screen ─────────────────────────────────────────────────────
    if (splash) {
        // Fade-out suave después de 1.8 segundos
        setTimeout(() => {
            splash.style.transition = "opacity 0.5s ease";
            splash.style.opacity = "0";
            // Ocultar completamente después del fade
            setTimeout(() => {
                splash.style.display = "none";
            }, 500);
        }, 1800);
    }

    // ── 2. Panel de Perfil Lateral ───────────────────────────────────────────

    /** Abre el panel de perfil desde la derecha */
    function abrirPanel() {
        if (panel) panel.classList.add("abierto");
        if (overlay) overlay.classList.add("visible");
        document.body.style.overflow = "hidden"; // Bloquear scroll
    }

    /** Cierra el panel de perfil */
    function cerrarPanel() {
        if (panel) panel.classList.remove("abierto");
        if (overlay) overlay.classList.remove("visible");
        document.body.style.overflow = ""; // Restaurar scroll
    }

    // Eventos para abrir/cerrar el panel
    if (btnHamb) btnHamb.addEventListener("click", abrirPanel);
    if (btnCerrar) btnCerrar.addEventListener("click", cerrarPanel);
    if (overlay) overlay.addEventListener("click", cerrarPanel); // Clic en overlay cierra

    // Cerrar con la tecla Escape
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") cerrarPanel();
    });

    // ── 3. Selección de Actividades ──────────────────────────────────────────
    if (lista) {
        lista.addEventListener("click", (ev) => {
            // Subir en el DOM hasta encontrar el elemento .actividad-item
            let item = ev.target;
            while (item && !item.classList.contains("actividad-item")) {
                item = item.parentElement;
            }
            if (!item) return;

            // Deseleccionar todos los items anteriores
            document.querySelectorAll(".actividad-item.selected").forEach((it) => {
                it.classList.remove("selected");
            });

            // Seleccionar el item actual
            item.classList.add("selected");
            const actividad = item.getAttribute("data-actividad");

            // Habilitar el botón "Comenzar"
            if (btnComenzar) {
                btnComenzar.disabled = false;
                btnComenzar.dataset.actividad = actividad || "";
            }
        });
    }

    // Al hacer clic en "Comenzar", ir al hub de juegos
    if (btnComenzar) {
        btnComenzar.addEventListener("click", () => {
            if (!btnComenzar.dataset.actividad) return;
            // Guardar origen para el botón "🏠 Inicio" en los juegos
            sessionStorage.setItem('juegos_origen', '/paciente/perfil');
            window.location.href = "/juegos/";
        });
    }
});
