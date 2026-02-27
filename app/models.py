from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Any, Optional


class UsuarioBase(BaseModel):
    """
    Datos de un usuario del sistema.
    """
    email: EmailStr
    activo: bool = True
    rol: str = Field(default="emisor", description="Rol del usuario: admin, doctor, emisor")
    estado: str = Field(default="activo", description="Estado del usuario: activo, ocupado, consulta")


class UsuarioCreate(UsuarioBase):
    """
    Datos necesarios para crear un usuario desde el registro.
    """
    password: str = Field(min_length=6, description="Contraseña en texto plano. Se debe encriptar en producción.")
    acepta_terminos: bool = True


class UsuarioPublico(UsuarioBase):
    """
    Representación pública del usuario (respuesta de API).
    """
    id: str = Field(alias="_id")


class ActividadCategoria(BaseModel):
    """
    Documento de la colección 'actividades'.
    """
    id: str = Field(alias="_id")
    categoria: str
    actividades: List[str]


class Asignacion(BaseModel):
    """
    Documento de la colección 'asignaciones'.

    BD,  actividades_asignadas' es un array de objetos así que lo modelamos
    como lista de diccionarios genéricos.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    medico_email: EmailStr
    actividades_asignadas: list[dict]  # <- importante!!!!! lista de objetos
    dificultad: str
    fecha_asignacion: datetime
    estado: str | None = None  # p.ej: "pendiente", "aceptada", "cancelada"


class ContenidoAdmin(BaseModel):
    """
    Documento de la colección 'contenido_admin'.
    Solo suele haber uno.
    """
    id: str = Field(alias="_id")
    imagenes: List[str]
    videos: List[str]
    audios_referencia: List[str]
    textos_sistema: List[str]
    instrucciones: Any | None = None


class HistorialActividad(BaseModel):
    """
    Documento de la colección 'historial_actividades'.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    categoria: str
    actividad: str
    puntos_obtenidos: int
    nivel: int
    fecha: datetime
    feedback: str | None = None


class PerfilPaciente(BaseModel):
    """
    Información extendida de un paciente (perfil).
    Se guarda en la colección 'perfiles_pacientes'.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    nombre: str
    edad: int
    escolaridad: str
    genero: str
    fecha_registro: datetime
    tutor: str
    parentesco: str


class SesionApp(BaseModel):
    """
    Registro de uso de la app por parte de un paciente.
    Colección: 'sesiones_app'..
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    fecha: datetime
    minutos_conectado: int


class ResultadoJuego(BaseModel):
    """
    Resultado de un juego completado por un paciente.
    Colección: 'resultados_juegos'.
    """
    id: str = Field(alias="_id")
    paciente_email: EmailStr
    categoria: str          # e.g. "articulacion", "resonancia", "respiracion"
    juego: str              # e.g. "letra_b", "veoveo", "globo"
    paso_completado: int    # last step completed (1-based)
    total_pasos: int
    completado: bool
    fecha: datetime
    notas: str | None = None