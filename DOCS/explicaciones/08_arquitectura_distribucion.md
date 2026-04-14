# Explicación: Arquitectura del Sistema FonoApp

**Archivos:** `diagrama_componentes.puml` y `diagrama_distribucion.puml`

## Descripción
Los modelos físicos o arquitectónicos de FonoApp. Explican de dónde provienen las carpetas locales `/app` y dónde "Viven" en el despliegue final una vez llevadas a producción con comandos para Start, Build y Deploy.

### Diagrama de Componentes (Carpetas internas FonoApp)
Describe la jerarquía top-down:
- **`Frontend (Cliente)`**: En las carpetas `/templates`, `/static/css`, y `/static/js` todo es estático o Renderizado en Jinja2. Usa fuertemente la `Web Audio API` para los pacientes (Voz) porque sin ella no ocurre la Fonoaudiología. No existe "React/Angular/Vue", el Client se conecta por HTTP puro.
- **`Backend (FastAPI)`**: Lo que abarca `/app/routers` en el directorio. Ellos no hablan de frente a Mongo -> le confieren esa orden a las clases del subdirectorio `/app/repositories`. 
- **`Bases de Datos`**: Conexión de API (App `Motor_AsyncIO`). 

**Conclusión Clave:** Una función de Frontend `JS` atada a un juego dinámico contacta a `/routers/juegos`, y este al repocitorio base. El Frontend vive y muere por sí solo por cada "pantalla".

### Diagrama de Distribución (Hardware o Nodos Nubes)
Mapeo de la Producción:
- **El Paciente / Médico (Node 1):** Usa navegadores como *Google Chrome* o *Safari (iOS)*, que interpretan la carpeta Frontend compilada al vuelo por el Servidor. Es hardware aislado (Laptops, Celulares).
- **El VPS / Render (Node 2):** Servidor Linux o PaaS que ejecuta Pydantic/Uvicorn bajo el Runtime de `Python 3.10+`. Mantiene escuchando y validando las APIS del backend.
- **MongoDB Atlas Cloud (Node 3):** Base de Datos remota. La conexión con Node 2 se sostiene por `protoloco mongodb+srv`. FonoApp puede escalar Node 2 a muchas replicas sin que Node 3 se sobresature inmediatamente, si respetamos AsyncIO.