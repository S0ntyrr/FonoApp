"""
FonoApp - Modelos Pydantic
==========================
Define los modelos de datos usados para validación y serialización.
Cada modelo corresponde a una colección en MongoDB.

Nota: Los documentos de MongoDB se almacenan como dicts.
      Estos modelos se usan para validar datos de entrada/salida.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Any, Optional


# ── Usuarios ───────────────────────────────────────────────────────────────────

class UsuarioBase(BaseModel):
    """
    Modelo base para todos los usuarios del sistema.
    Colección MongoDB: 'usuarios'
    
    Roles disponibles:
    - 'admin': Administrador con acceso completo
    - 'medico': Médico/terapeuta que evalúa pacientes
    - 'paciente': Paciente que realiza los juegos
    - 'emisor': Rol auxiliar (placeholder)
    
    Estados disponibles (para médicos):
    - 'activo': Disponible para recibir asignaciones
    - 'ocupado': No disponible temporalmente
    - 'consulta': En sesión activa con un paciente
    """
    nombre: str = Field(default="", description="Nombre completo del usuario")
    email: EmailStr
    activo: bool = True
    rol: str = Field(default="emisor", description="Rol del usuario: admin, medico, paciente, emisor")
    estado: str = Field(default="activo", description="Estado del usuario: activo, ocupado, consulta")


class UsuarioCreate(UsuarioBase):
    """
    Datos necesarios para crear un nuevo usuario.
    Usado en el formulario de registro y en el panel admin.
    
    IMPORTANTE: La contraseña se almacena en texto plano.
    En producción, usar bcrypt o similar para encriptarla.
    """
    password: str = Field(min_length=6, description="Contraseña (mínimo 6 caracteres)")
    acepta_terminos: bool = True


class UsuarioPublico(UsuarioBase):
    """
    Representación pública del usuario (sin contraseña).
    Usado en respuestas de API.
    """
    id: str = Field(alias="_id")


# ── Actividades ────────────────────────────────────────────────────────────────

class ActividadCategoria(BaseModel):
    """
    Categoría de actividades/juegos.
    Colección MongoDB: 'actividades'
    
    Categorías actuales:
    - respiracion: Infla el globo, El molino de Pepe
    - fonacion: ¡Haz un gol!, Escala musical
    - resonancia: Escaleras, Piano, ¡Veo veo!
    - articulacion: Letras B/D/F/R, Completa la palabra, Moto
    - prosodia: Adivina el animal, Trabalenguas, Adivinanza, Canción
    - discriminacion_auditiva: Sonidos animales/objetos, Arrastra
    - practica_conmigo: Rompecabezas, Cara, Asociación
    
    Para actualizar la BD con los juegos reales:
    GET /juegos/seed-actividades
    """
    id: str = Field(alias="_id")
    categoria: str
    actividades: List[str]


# ── Asignaciones ───────────────────────────────────────────────────────────────

class Asignacion(BaseModel):
    """
    Asignación de un médico a un paciente.
    Colección MongoDB: 'asignaciones'
    
    Estados:
    - 'pendiente': Creada por el admin, esperando que el médico acepte
    - 'aceptada': El médico aceptó y está atendiendo al paciente
    - 'cancelada': El médico rechazó o se canceló la asignación
    
    Tipos:
    - 'automatica': El sistema eligió el médico al azar
    - 'manual': El admin eligió el médico específico
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    medico_email: EmailStr
    actividades_asignadas: list[dict]  # Lista de {categoria, actividad}
    dificultad: str  # 'facil', 'media', 'dificil'
    fecha_asignacion: datetime
    estado: str | None = None
    tipo: str | None = None  # 'automatica' o 'manual'


# ── Contenido del sistema ──────────────────────────────────────────────────────

class ContenidoAdmin(BaseModel):
    """
    Contenido multimedia del sistema.
    Colección MongoDB: 'contenido_admin' (solo hay un documento)
    
    Gestionado desde /admin/contenido con 3 tabs:
    - Textos: instrucciones, avisos, reglas
    - Media: imágenes y videos subidos
    - Juegos: referencia de juegos implementados
    """
    id: str = Field(alias="_id")
    imagenes: List[str]           # Rutas a imágenes en /static/uploads/
    videos: List[str]             # Rutas a videos en /static/uploads/
    audios_referencia: List[str]  # Rutas a audios de referencia
    textos_sistema: List[Any]     # Lista de {texto, tipo, fecha}
    instrucciones: Any | None = None


# ── Historial de actividades ───────────────────────────────────────────────────

class HistorialActividad(BaseModel):
    """
    Registro de una actividad completada por un paciente.
    Colección MongoDB: 'historial_actividades'
    
    Se crea automáticamente cuando:
    - El paciente completa un juego (POST /juegos/resultado con completado=true)
    
    El médico puede:
    - Ver actividades sin feedback en /doctor/evaluaciones-pendientes
    - Agregar feedback desde el formulario de evaluación
    
    feedback=None indica que está pendiente de evaluación.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    categoria: str      # Categoría del juego (respiracion, articulacion, etc.)
    actividad: str      # Nombre del juego completado
    puntos_obtenidos: int
    nivel: int
    fecha: datetime
    feedback: str | None = None  # Evaluación del médico (None = pendiente)


# ── Perfil del paciente ────────────────────────────────────────────────────────

class PerfilPaciente(BaseModel):
    """
    Información extendida del paciente.
    Colección MongoDB: 'perfiles_pacientes'
    
    Se crea/actualiza desde /paciente/perfil (panel lateral del paciente).
    Incluye datos del tutor/cuidador ya que los pacientes suelen ser menores.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    nombre: str
    edad: int
    escolaridad: str    # Preescolar, Primaria, Secundaria, Bachillerato, Universidad, Otro
    genero: str         # Masculino, Femenino, Otro
    fecha_registro: datetime
    tutor: str          # Nombre del tutor/cuidador
    parentesco: str     # Relación con el paciente (Madre, Padre, Abuelo, etc.)


# ── Sesiones de uso ────────────────────────────────────────────────────────────

class SesionApp(BaseModel):
    """
    Registro de uso diario de la app por un paciente.
    Colección MongoDB: 'sesiones_app'
    
    Usado para mostrar el calendario de uso en el dashboard del paciente.
    Un documento por día y paciente.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    fecha: datetime
    minutos_conectado: int


# ── Resultados de juegos ───────────────────────────────────────────────────────

class ResultadoJuego(BaseModel):
    """
    Resultado detallado de un juego completado (o en progreso).
    Colección MongoDB: 'resultados_juegos'
    
    Se crea automáticamente via POST /juegos/resultado
    llamado desde el JavaScript de cada juego al completarse.
    
    Cuando completado=True, también se crea un registro en historial_actividades
    para que el médico pueda evaluarlo.
    
    Categorías de juegos:
    - respiracion: globo, molino
    - fonacion: gol, escala
    - resonancia: escaleras, piano, veoveo
    - articulacion: letra_b, letra_d, letra_f, letra_r, completa_palabra, moto_voz
    - prosodia: adivina_animal, trabalenguas, adivinanza_imagen, completa_cancion
    - discriminacion_auditiva: sonidos_animales, sonidos_objetos, arrastra_sonido
    - practica_conmigo: rompecabezas, cara, asociacion
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    categoria: str          # Categoría del juego
    juego: str              # Nombre específico del juego
    paso_completado: int    # Último paso completado (1-based)
    total_pasos: int        # Total de pasos del juego
    completado: bool        # True si el juego fue completado exitosamente
    fecha: datetime
    notas: str | None = None
    puntos: int = 0         # Puntos obtenidos en el juego
    nivel: int = 1          # Nivel del paciente al momento de jugar
