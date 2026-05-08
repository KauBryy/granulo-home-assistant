from homeassistant.components.text import TextEntity
from .const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

async def async_setup_entry(hass, entry, async_add_entities):
    user_id = entry.data["user_id"]
    async_add_entities([
        GranuloInputText(user_id, "note", "Granulo Poele Note", "mdi:text")
    ])

class GranuloInputText(TextEntity):
    def __init__(self, user_id, key, name, icon):
        self.user_id = user_id
        self.key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_input_v1_{user_id}_{key}"
        self._attr_native_value = ""

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.user_id)},
            name="Poêle Granulo",
            manufacturer="Granulo App",
            model="Expert Mode",
        )

    async def async_set_value(self, value: str) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
