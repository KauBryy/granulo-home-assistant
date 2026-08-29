import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs Granulo depuis le coordinateur central."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors_config = [
        ("stock_actuel", "sacs", "mdi:package-variant"),
        ("stock_kg", "kg", "mdi:weight-kilogram"),
        ("achats_saison", "sacs", "mdi:cart-outline"),
        ("brulages_saison", "sacs", "mdi:fire"),
        ("achats_total", "sacs", "mdi:archive-arrow-down"),
        ("brulages_total", "sacs", "mdi:fire-alert"),
        ("depenses_saison", "€", "mdi:cash-fast"),
        ("depenses_total", "€", "mdi:cash-lock"),
        ("moyenne_7j", "kg/j", "mdi:chart-line"),
        ("moyenne_mois", "kg/j", "mdi:calendar-month"),
        ("moyenne_saison", "kg/j", "mdi:snowflake"),
        ("jours_restants", "jours", "mdi:clock-end"),
        ("vitre", "sacs", "mdi:mirror"),
        ("entretien", "sacs", "mdi:wrench"),
    ]

    entities = [GranuloSensor(coordinator, key, unit, icon) for key, unit, icon in sensors_config]
    async_add_entities(entities)

class GranuloSensor(CoordinatorEntity, SensorEntity):
    """Capteur individuel Granulo lié au DataUpdateCoordinator."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, key, unit, icon):
        super().__init__(coordinator)
        self.key = key
        self._attr_translation_key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_v4_{coordinator.user_id}_{key}"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        if "error" in self.coordinator.data:
            return self.coordinator.data["error"]
        return self.coordinator.data.get(self.key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id)},
            name="Poêle Granulo",
            manufacturer="Granulo App",
            model="Expert Mode",
        )
