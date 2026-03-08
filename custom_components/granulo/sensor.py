import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTime
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration des capteurs Granulo."""
    # Ces capteurs seront mis à jour via le Push de l'app mobile
    sensors = [
        GranuloSensor("Stock", "stock", "sacs", "mdi:package-variant"),
        GranuloSensor("Achats", "achat", "sacs", "mdi:cart-arrow-down"),
        GranuloSensor("Brûlages", "brulage", "sacs", "mdi:fire"),
        GranuloSensor("Autonomie", "autonomie", "jours", "mdi:clock-end"),
        GranuloSensor("Depuis Vitre", "vitre", "sacs", "mdi:shimmer"),
        GranuloSensor("Depuis Entretien", "entretien", "sacs", "mdi:wrench-clock"),
    ]
    async_add_entities(sensors)

class GranuloSensor(SensorEntity):
    """Représentation d'un capteur Granulo."""

    def __init__(self, name, type, unit, icon):
        self._attr_name = f"Granulo {name}"
        self._attr_unique_id = f"granulo_{type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._type = type
        self._state = None

    @property
    def state(self):
        """Retourne l'état actuel (si HA a déjà reçu une valeur)."""
        # On essaie de récupérer l'état stocké dans HA s'il existe
        return self._state
