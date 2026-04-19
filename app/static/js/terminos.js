/**
 * Script para manejar la apertura de términos y condiciones en modal
 * Permite al usuario leer los términos sin salir del formulario de registro
 */

function abrirTerminos(event) {
    event.preventDefault();
    
    // Crear el modal
    const modal = document.createElement('div');
    modal.id = 'modal-terminos';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    
    // Contenedor del modal
    const contenedor = document.createElement('div');
    contenedor.style.cssText = `
        background-color: white;
        border-radius: 8px;
        max-width: 90vw;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    `;
    
    // Header del modal
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 1.5rem;
        border-bottom: 2px solid #d32f2f;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    header.innerHTML = `
        <h2 style="margin: 0; color: #d32f2f; font-size: 1.3rem;">Términos y Condiciones</h2>
        <button onclick="cerrarModalTerminos()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #666;">×</button>
    `;
    
    // Cuerpo del modal (iframe para los términos)
    const cuerpo = document.createElement('div');
    cuerpo.style.cssText = `
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
    `;
    
    // Cargar los términos mediante AJAX
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/auth/terminos-condiciones', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Extraer solo el contenido del bloque de términos
            const parser = new DOMParser();
            const htmlDoc = parser.parseFromString(xhr.responseText, 'text/html');
            const seccion = htmlDoc.querySelector('section.pantalla-movil');
            
            if (seccion) {
                // Limpiar el contenedor de botones del original
                const botonesDiv = seccion.querySelector('div:last-child');
                if (botonesDiv && botonesDiv.style.display === '' && botonesDiv.querySelector('.boton-rojo')) {
                    botonesDiv.remove();
                }
                cuerpo.appendChild(seccion);
            }
        }
    };
    xhr.send();
    
    // Footer del modal
    const footer = document.createElement('div');
    footer.style.cssText = `
        padding: 1rem 1.5rem;
        border-top: 1px solid #eee;
        display: flex;
        gap: 0.8rem;
        justify-content: flex-end;
    `;
    footer.innerHTML = `
        <button onclick="cerrarModalTerminos()" style="padding: 0.7rem 1.5rem; background-color: #90a4ae; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">Cerrar</button>
        <button onclick="aceptarTerminos()" style="padding: 0.7rem 1.5rem; background-color: #d32f2f; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">He leído y acepto</button>
    `;
    
    // Armar el modal
    contenedor.appendChild(header);
    contenedor.appendChild(cuerpo);
    contenedor.appendChild(footer);
    modal.appendChild(contenedor);
    
    // Agregar al DOM
    document.body.appendChild(modal);
    
    // Prevenir scroll del fondo
    document.body.style.overflow = 'hidden';
}

function cerrarModalTerminos() {
    const modal = document.getElementById('modal-terminos');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}

function aceptarTerminos() {
    // Marcar el checkbox como aceptado
    const checkbox = document.getElementById('acepta_terminos');
    if (checkbox) {
        checkbox.checked = true;
    }
    cerrarModalTerminos();
}

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(event) {
    const modal = document.getElementById('modal-terminos');
    if (modal && event.target === modal) {
        cerrarModalTerminos();
    }
});

// Cerrar modal con tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModalTerminos();
    }
});
