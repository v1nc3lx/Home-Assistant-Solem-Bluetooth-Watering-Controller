import random
import uuid
from datetime import datetime
from homeassistant.util import dt as dt_util

def mac_to_uuid(mac: str, last_part: int ) -> str:
    # Remover os dois pontos do MAC Address
    mac_numbers = mac.replace(':', '')
    
    # Pegar os 12 primeiros dígitos do MAC para formar a parte fixa do UUID
    x_part = f"{mac_numbers[:4]}-{mac_numbers[4:8]}-{mac_numbers[8:12]}"
    
    # Gerar um número aleatório para os últimos 3 dígitos (YYY)
    yyy_part = f"{last_part:03d}"
    
    return f"{x_part}-{yyy_part}"

def ensure_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.min  # Se o formato for inválido, usa datetime.min
    return datetime.min  # Se for None ou outro tipo inesperado
    
def ensure_aware(dt_obj: datetime | None) -> datetime | None:
    """Ensure datetime is timezone-aware."""
    if dt_obj and dt_obj.tzinfo is None:
        return dt_util.as_local(dt_obj)
    return dt_obj