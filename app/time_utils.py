from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import settings


def _app_zone() -> ZoneInfo:
    """Return configured application timezone, falling back to UTC if invalid."""
    try:
        return ZoneInfo(settings.APP_TIMEZONE)
    except Exception:
        return ZoneInfo("UTC")


def app_now() -> datetime:
    """Current app-local datetime as naive value for Mongo date-range compatibility."""
    return datetime.now(_app_zone()).replace(tzinfo=None)


def day_bounds(fecha_base: datetime) -> tuple[datetime, datetime]:
    """Day start and end boundaries for the provided local date."""
    inicio = datetime(fecha_base.year, fecha_base.month, fecha_base.day)
    return inicio, inicio + timedelta(days=1)
