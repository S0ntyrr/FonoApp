from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .config import settings


def _app_zone():
    """Return configured application timezone; falls back to stdlib UTC (no tzdata needed) if unavailable."""
    try:
        return ZoneInfo(settings.APP_TIMEZONE)
    except Exception:
        return timezone.utc


def app_now() -> datetime:
    """Current app-local datetime as naive value for Mongo date-range compatibility."""
    return datetime.now(_app_zone()).replace(tzinfo=None)


def day_bounds(fecha_base: datetime) -> tuple[datetime, datetime]:
    """Day start and end boundaries for the provided local date."""
    inicio = datetime(fecha_base.year, fecha_base.month, fecha_base.day)
    return inicio, inicio + timedelta(days=1)
