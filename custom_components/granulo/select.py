from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GranuloBrandSelect(coordinator)])

class GranuloBrandSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "marque"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"granulo_select_v1_{coordinator.user_id}_brand"
        self._attr_icon = "mdi:tag-outline"
        self._current_option = None

    @property
    def options(self) -> list[str]:
        """Retourne la liste des marques disponibles configurées dans Granulo."""
        if self.coordinator.data and isinstance(self.coordinator.data, dict):
            brands = self.coordinator.data.get("custom_brands")
            if not brands and "data" in self.coordinator.data and isinstance(self.coordinator.data["data"], dict):
                brands = self.coordinator.data["data"].get("custom_brands")
            if brands and isinstance(brands, list) and len(brands) > 0:
                return list(brands)
        return ["Générique"]

    @property
    def current_option(self) -> str:
        """Retourne la marque actuellement sélectionnée."""
        opts = self.options
        if self._current_option in opts:
            return self._current_option
        return opts[0] if opts else "Générique"

    async def async_select_option(self, option: str) -> None:
        """Change la marque sélectionnée."""
        self._current_option = option
        self.async_write_ha_state()

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id)},
            name="Granulo Poele",
            manufacturer="Granulo App",
            model="Expert Mode",
        )
