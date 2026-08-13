# 🎙️ FonoApp

> Una app web para hacer la terapia de fonoaudiología más divertida, interactiva y fácil de seguir.

---

## ¿Qué es FonoApp?

FonoApp conecta a **pacientes**, **médicos** y **administradores** en un solo lugar. Los pacientes practican sus ejercicios jugando, los médicos revisan cómo van y dan retroalimentación, y el administrador coordina todo el proceso.

---

## 👥 ¿Quién usa la app?

| Rol | ¿Qué hace? |
|-----|-----------|
| 🧒 **Paciente** | Juega, practica y ve su progreso diario |
| 🩺 **Médico** | Revisa avances, evalúa y da feedback |
| 🛡️ **Administrador** | Gestiona usuarios, asignaciones y el sistema |

---

## 🎮 Los juegos (23 juegos en 7 categorías)

**🌬️ Respiración**
- Infla el globo — sopla para inflarlo con el micrófono
- El molino de Pepe — ayuda a Pepe soplando

**🎵 Fonación**
- ¡Haz un gol! — grita "goooool" para marcar
- Escala musical — imita sonidos con una flauta

**🔊 Resonancia**
- Escaleras — sube o baja según tu tono de voz
- Piano Estrellita — toca y luego canta
- ¡Veo, veo! — encuentra la imagen y nómbrala

**🗣️ Articulación**
- Letras B, D, F y R — pronunciación paso a paso
- Completa la palabra — escribe la letra que falta
- ¡Acelera la moto! — habla fuerte para acelerar

**🎤 Prosodia**
- Adivina el animal — activa el micrófono, 4 intentos
- Trabalenguas — lee y registra palabras difíciles
- Relaciona la adivinanza — escucha y toca la imagen
- Completa la canción — canta la parte que falta

**👂 Discriminación Auditiva**
- Sonidos de animales — escucha y elige el animal
- Sonidos de objetos — escucha y selecciona el objeto
- Arrastra al sonido — arrastra la imagen correcta

**🧩 Practica Conmigo**
- Rompecabezas de letras y animales
- Crea tu personaje — arrastra partes del rostro
- Asociación de imágenes

---

## 🔄 ¿Cómo funciona?

```
1. El paciente inicia sesión y ve su dashboard
2. Ve 4 actividades aleatorias del día (de diferentes categorías)
3. Hace clic en una actividad → va al juego
4. Al completar el juego → se guarda automáticamente en la base de datos
5. Al volver al dashboard → la actividad se marca como ✓ completada
6. Cuando completa todas → "¡Excelente! Vuelve mañana para nuevas actividades"
7. El médico revisa los resultados y da feedback
8. El admin supervisa todo desde su panel
```

---

## 🏠 Pantallas principales

### Paciente
- Dashboard con bienvenida personalizada
- 4 actividades aleatorias del día (cambian cada día)
- Acceso rápido a todos los juegos
- Calendario de uso mensual
- Progreso visual (✓ completado / pendiente)

### Médico
- Panel con estado (disponible / ocupado / en consulta)
- Lista de pacientes con progreso en juegos
- Perfil detallado con gráfica de avance por categoría
- Evaluaciones pendientes con formulario de feedback
- Historial completo de actividades

### Administrador
- Dashboard con estadísticas en tiempo real
- Gestión de pacientes y médicos (CRUD completo)
- Asignaciones: automática o manual
- Historial con barras de progreso por categoría
- Resultados de juegos con estadísticas de aciertos
- Contenido del sistema: textos, imágenes, videos

---

## 📊 Base de datos (MongoDB Atlas)

Las colecciones principales:

| Colección | ¿Para qué? |
|-----------|-----------|
| `usuarios` | Pacientes, médicos y admins |
| `perfiles_pacientes` | Datos del perfil del paciente |
| `actividades` | Catálogo de juegos por categoría |
| `asignaciones` | Médico asignado a cada paciente |
| `resultados_juegos` | Resultados de cada juego jugado |
| `historial_actividades` | Actividades completadas (para el médico) |
| `sesiones_app` | Días y minutos de uso |
| `contenido_admin` | Textos, imágenes y videos del sistema |

---

## 🔒 Accesos

- El **paciente** ve su perfil y sus juegos
- El **médico** ve sus pacientes asignados y sus resultados
- El **administrador** tiene acceso completo al sistema

---

## 🛠️ Hecho con

| Herramienta | Para qué |
|-------------|---------|
| FastAPI | El servidor web |
| MongoDB Atlas | La base de datos en la nube |
| Jinja2 | Las pantallas HTML |
| Python 3.11+ | El lenguaje principal |

---

## ▲ Despliegue en Vercel

Este proyecto quedó preparado para Vercel con:

- [vercel.json](C:/Users/santy/Desktop/CC/FonoApp/vercel.json)
- [api/index.py](C:/Users/santy/Desktop/CC/FonoApp/api/index.py)

### Variables de entorno mínimas

- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `SESSION_SECRET_KEY`
- `SESSION_HTTPS_ONLY=true` (recomendado en producción)

### Pasos rápidos

1. Conecta el repositorio en Vercel.
2. Configura las variables de entorno.
3. Deploy.

> Nota: los archivos subidos en `app/static/uploads` se guardan en filesystem local del runtime. En producción serverless se recomienda moverlos a almacenamiento externo (S3, Cloudinary, etc.).

---

## 📁 Documentación

En la carpeta [`DOCS/`](DOCS/) hay diagramas del sistema:
- Roles y responsabilidades de cada usuario
- Qué puede hacer cada uno
- Cómo están organizados los datos
- Ciclo de vida de cada elemento

---

> *"La terapia más efectiva es la que el paciente disfruta hacer."* 🎙️
