from homeassistant.components.number import NumberEntity
from .const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        GranuloInputNumber(coordinator, "quantite", "Granulo Poele Quantite", "sacs", "mdi:numeric", 1, 1000),
        GranuloInputNumber(coordinator, "prix", "Granulo Poele Prix", "€", "mdi:currency-eur", 0, 10000)
    ])

class GranuloInputNumber(NumberEntity):
    def __init__(self, coordinator, key, name, unit, icon, min_val, max_val):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_input_v1_{coordinator.user_id}_{key}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = 1.0 if key == "quantite" else 0.01
        self._attr_native_value = 1.0 if key == "quantite" else 0.0
        self._attr_mode = "box"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id)},
            name="Poêle Granulo",
            manufacturer="Granulo App",
            model="Expert Mode",
        )

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
