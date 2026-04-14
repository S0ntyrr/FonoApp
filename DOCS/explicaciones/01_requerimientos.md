# Explicación: Requerimientos del Sistema (Funcionales y No Funcionales)

**Archivo:** `requerimientos.txt`

## Descripción
Este documento lista todos los requerimientos que definen el comportamiento (Funcionales) y las restricciones o calidades (No Funcionales) que debe tener FonoApp para considerarse un producto terminado.

### Requerimientos Funcionales (RF)
Son todas las funciones operativas del sistema. FonoApp consta de varios módulos:
- **Autenticación (RF-01):** Cómo un usuario se loguea y como la app sabe a dónde dirigirlo según su rol.
- **Módulo de Paciente (RF-02):** Todo lo que el niño/paciente puede hacer (ver perfil, entrar al hub de juegos, completar las actividades diarias o asignadas).
- **Módulo de Juegos (RF-03):** Cómo interactúan y se desarrollan los juegos, su estructuración en *n* categorías (diseñado para ser escalable).
- **Módulo de Médico (RF-04):** Permite revisar el historial de pacientes, asignarles terapias específicas, ver aciertos y dejar retroalimentación.
- **Módulo Administrador (RF-05):** Cuentas maestras que administran altas, bajas y el contenido multimedia de la plataforma FonoApp.
- **Gestión de Base de datos (RF-06):** Reglas para almacenar resultados asegurando un registro histórico inmodificable del niño.

### Requerimientos No Funcionales (RNF)
Se enlistan bajo 12 rubros requeridos en el estándar de calidad de arquitectura de software:
1. **Rendimiento** (tiempos de respuesta web)
2. **Usabilidad** (responsive en web-mobile, flujos fáciles para niños)
3. **Seguridad** (encriptación, caducidad de sesión)
4. **Disponibilidad** (24/7 cloud)
5. **Mantenibilidad** (documentación y diseño de arquitectura mantenible)
6. **Compatibilidad** (Navegadores Chrome, iOS/Android navegadores web)
7. **Escalabilidad** (Habilidad de agregar nuevos juegos sin reprogramar controladores backend)
8. **Confiabilidad** (Tolerancia a fallas de red en la mitad de un juego)
9. **Portabilidad** (Dockerizable / fácilmente migrado a la nube)
10. **Interoperabilidad** (Pensar en endpoints REST)
11. **Localización** (ES-LATAM por defecto)
12. **Restricciones Éticas/Legales** (Cumplimiento GDPR/HIPAA para anonimato en menores).