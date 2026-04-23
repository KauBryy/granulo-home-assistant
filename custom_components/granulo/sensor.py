import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuration des capteurs Granulo."""
    device_id = config_entry.entry_id
    device_name = config_entry.data.get("name", "Mon Assistant Granulo")

    sensors = [
        # --- États & Maintenance ---
        GranuloSensor(device_id, device_name, "Stock", "stock", "sacs", "mdi:package-variant"),
        GranuloSensor(device_id, device_name, "Autonomie", "autonomie", "jours", "mdi:clock-end"),
        GranuloSensor(device_id, device_name, "Depuis dernier Vitre", "vitre", "sacs", "mdi:shimmer"),
        GranuloSensor(device_id, device_name, "Depuis dernier Entretien", "entretien", "sacs", "mdi:wrench-clock"),
        
        # --- Saison Actuelle ---
        GranuloSensor(device_id, device_name, "Achats Saison", "achat_saison", "sacs", "mdi:cart-arrow-down"),
        GranuloSensor(device_id, device_name, "Brûlages Saison", "brulage_saison", "sacs", "mdi:fire"),
        GranuloSensor(device_id, device_name, "Dépenses Saison", "depense_saison", "€", "mdi:cash-multiple"),
        
        # --- Depuis Toujours ---
        GranuloSensor(device_id, device_name, "Achats Total", "achat_total", "sacs", "mdi:archive-arrow-down"),
        GranuloSensor(device_id, device_name, "Brûlages Total", "brulage_total", "sacs", "mdi:fire-alert"),
        GranuloSensor(device_id, device_name, "Dépenses Totales", "depense_total", "€", "mdi:cash-lock"),
        
        # --- Stats ---
        GranuloSensor(device_id, device_name, "Moyenne 7j", "moyenne_7j", "kg/j", "mdi:chart-line"),
        GranuloSensor(device_id, device_name, "Moyenne Mois", "moyenne_mois", "kg/j", "mdi:calendar-month"),
        GranuloSensor(device_id, device_name, "Moyenne Saison", "moyenne_saison", "kg/j", "mdi:weather-snowy"),
    ]
    async_add_entities(sensors)

class GranuloSensor(SensorEntity):
    def __init__(self, device_id, device_name, name, type, unit, icon):
        self._device_id = device_id
        self._device_name = device_name
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"granulo_{device_id}_{type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._type = type
        self._state = None

    @property
    def check_is_valid(self):
        return True

    @property
    def device_info(self):
        """Assigne ce capteur à un appareil dans Home Assistant."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Granulo App",
            "model": "Poêle Connecté",
        }

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        """Appelé quand le capteur est ajouté à HA."""
        # On écoute les données de l'événement dispatcher configuré dans __init__.py
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, 
                f"{DOMAIN}_update_{self._device_id}", 
                self._handle_update
            )
        )

    def _handle_update(self, data):
        """Met à jour l'état si une donnée nous concerne."""
        if self._type in data:
            val = data[self._type]
            if val is not None:
                self._state = val
                self.async_write_ha_state()
