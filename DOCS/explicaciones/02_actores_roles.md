# Explicación: Definición de Actores y Roles

**Archivo:** `actores_roles.puml`

## Descripción
Este diagrama define quién usa el sistema y qué fronteras de sistema no deben cruzar. De un solo vistazo se identifican 4 diferentes actores interactuando y sus permisos en `FonoApp`.

### Actores
1. **Admin (`rol: admin`):** 
   - Dirige la plataforma y la gestiona a nivel general. Puede crear y modificar de todo (médicos, pacientes, juegos y textos/contenido principal del sistema).
   - *Rutas:* `/admin/*`
2. **Médico (`rol: medico`):** 
   - Es el terapeuta responsable clínico. Verifica historias de pacientes para darles retroalimentación técnica (Feedback), asignar un lote de tareas obligatorias para casa, y consultar métricas para evaluar los resultados terapéuticos.
   - *Rutas:* `/doctor/*`
3. **Paciente (`rol: paciente`):** 
   - Son el cliente y usuario principal de impacto, especialmente niños o menores, acompañados de su tutor. Tienen la pantalla de visualización del *Hub de Juegos* simplificada e interactiva orientada a la gamificación y realización de terapia de fonoaudiología en el hogar.
   - *Rutas:* `/paciente/*`, `/juegos/*`
4. **Emisor (`rol: emisor`):**
   - Una cuenta comodín o rol complementario actualmente pensado para el escalamiento de contenido externo o supervisión familiar más detallada. 
   - *Rutas:* `/emisor/*`

### Relación al Sistema Completo
Al entender que FonoApp tiene permisos limitados, se justifica claramente por qué el Backend tiene rutas divididas modularmente. Este diagrama muestra el ecosistema completo desde el punto de vista humano.