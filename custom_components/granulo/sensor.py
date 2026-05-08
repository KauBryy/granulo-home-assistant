import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs Granulo depuis le coordinateur central."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors_config = [
        ("stock_actuel", "Granulo Poele Stock Actuel", "sacs", "mdi:package-variant"),
        ("stock_kg", "Granulo Poele Stock (kg)", "kg", "mdi:weight-kilogram"),
        ("achats_saison", "Granulo Poele Achats Saison", "sacs", "mdi:cart-outline"),
        ("brulages_saison", "Granulo Poele Brûlages Saison", "sacs", "mdi:fire"),
        ("achats_total", "Granulo Poele Achats Total", "sacs", "mdi:archive-arrow-down"),
        ("brulages_total", "Granulo Poele Brûlages Total", "sacs", "mdi:fire-alert"),
        ("depenses_saison", "Granulo Poele Dépenses Saison", "€", "mdi:cash-fast"),
        ("depenses_total", "Granulo Poele Dépenses Total", "€", "mdi:cash-lock"),
        ("moyenne_7j", "Granulo Poele Moyenne 7j", "kg/j", "mdi:chart-line"),
        ("moyenne_mois", "Granulo Poele Moyenne Mois", "kg/j", "mdi:calendar-month"),
        ("moyenne_saison", "Granulo Poele Moyenne Saison", "kg/j", "mdi:snowflake"),
        ("jours_restants", "Granulo Poele Jours Restants", "jours", "mdi:clock-end"),
        ("vitre", "Granulo Poele Vitre", "sacs", "mdi:mirror"),
        ("entretien", "Granulo Poele Entretien", "sacs", "mdi:wrench"),
    ]

    entities = [GranuloSensor(coordinator, *cfg) for cfg in sensors_config]
    async_add_entities(entities)

class GranuloSensor(SensorEntity):
    def __init__(self, coordinator, key, name, unit, icon):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_v4_{coordinator.user_id}_{key}"

    @property
    def state(self):
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

    @property
    def should_poll(self): return False

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
