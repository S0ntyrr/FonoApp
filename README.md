# 🎙️ FonoApp

> Una app web para hacer la terapia de fonoaudiología más divertida, interactiva y fácil de seguir.

---

## ¿Qué es FonoApp?

FonoApp conecta a **pacientes**, **médicos** y **administradores** en un solo lugar. Los pacientes practican sus ejercicios jugando, los médicos revisan cómo van y dan retroalimentación, y el administrador coordina todo el proceso.

---

## 👥 ¿Quién usa la app?

| Rol | ¿Qué hace? |
|-----|-----------|
| 🧒 **Paciente** | Juega, practica y ve su progreso |
| 🩺 **Médico** | Revisa avances y da feedback |
| 🛡️ **Administrador** | Gestiona usuarios y el sistema |

---

## 🎮 Los juegos

Los pacientes practican a través de juegos organizados en 5 categorías:

**🌬️ Respiración**
- Infla el globo — sopla para inflarlo
- El molino de Pepe — ayuda a Pepe soplando

**🎵 Fonación**
- ¡Haz un gol! — grita "goooool" para marcar
- Escala musical — imita sonidos con una flauta

**🔊 Resonancia**
- Escaleras — sube o baja según tu tono de voz
- Piano Estrellita — toca y luego canta
- ¡Veo, veo! — encuentra la imagen y nómbrala

**🗣️ Articulación**
- Juegos para practicar las letras B, D, F y R

**🧩 Practica Conmigo**
- Rompecabezas de letras y animales
- Crea tu personaje — arrastra partes del rostro
- Asociación de imágenes

---

## 🔄 ¿Cómo funciona?

```
1. El paciente inicia sesión y ve su dashboard
2. Juega los ejercicios fonoaudiológicos
3. Los resultados se guardan automáticamente
4. El admin asigna un médico al paciente
5. El médico revisa los resultados y da feedback
6. El admin supervisa todo desde su panel
```

---

## 🏠 Pantallas principales

### Paciente
- Dashboard con bienvenida personalizada
- Acceso rápido a todos los juegos
- Lista de actividades asignadas por su médico
- Calendario de uso mensual

### Médico
- Panel con su estado (disponible / ocupado / en consulta)
- Lista de pacientes con su progreso en juegos
- Perfil detallado de cada paciente con gráfica de avance
- Evaluaciones pendientes con formulario de feedback
- Historial completo de actividades

### Administrador
- Dashboard con estadísticas del sistema
- Gestión de pacientes y médicos (crear, editar, eliminar)
- Asignaciones: automática (el sistema elige) o manual (tú eliges)
- Historial de actividades con barras de progreso por categoría
- Resultados de juegos con estadísticas de aciertos por juego y por paciente
- Contenido del sistema: textos, imágenes, videos y referencia de juegos

---

## 📊 Lo que registra el sistema

Cada vez que un paciente juega, se guarda:
- ✅ Si completó el juego o quedó a medias
- 📈 Cuántos pasos completó
- 🗓️ Fecha y hora de la sesión

El médico puede ver todo esto y escribir su evaluación directamente desde la app.

---

## 🔒 Accesos

Cada usuario solo ve lo que le corresponde:
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

## 📁 Documentación

En la carpeta [`DOCS/`](DOCS/) hay diagramas del sistema:
- Roles y responsabilidades de cada usuario
- Qué puede hacer cada uno
- Cómo están organizados los datos
- Ciclo de vida de cada elemento

---

> *"La terapia más efectiva es la que el paciente disfruta hacer."* 🎙️
