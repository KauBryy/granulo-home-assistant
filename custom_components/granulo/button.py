from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
from homeassistant.helpers.entity import DeviceInfo

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        GranuloActionButton(coordinator, "burn", "Granulo Poele Enregistrer un Brulage", "mdi:fire"),
        GranuloActionButton(coordinator, "purchase", "Granulo Poele Enregistrer un Achat", "mdi:cart")
    ])

class GranuloActionButton(ButtonEntity):
    def __init__(self, coordinator, action_type, name, icon):
        self.coordinator = coordinator
        self.action_type = action_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_btn_{coordinator.user_id}_{action_type}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id)},
            name="Poêle Granulo",
            manufacturer="Granulo App",
            model="Expert Mode",
        )

    async def async_press(self) -> None:
        """Appelé quand on appuie sur le bouton."""
        # 1. Récupérer les valeurs des inputs
        # On cherche les entités number et text créées par notre intégration
        qty_entity = f"number.granulo_poele_quantite"
        price_entity = f"number.granulo_poele_prix"
        note_entity = f"text.granulo_poele_note"

        qty = float(self.hass.states.get(qty_entity).state or 1.0) if self.hass.states.get(qty_entity) else 1.0
        price = float(self.hass.states.get(price_entity).state or 0.0) if self.hass.states.get(price_entity) else 0.0
        note = self.hass.states.get(note_entity).state if self.hass.states.get(note_entity) else "Ajouté via Home Assistant"

        # 2. Appeler le service correspondant
        service_data = {"amount": qty, "note": note}
        if self.action_type == "purchase":
            service_data["price"] = price
            await self.hass.services.async_call(DOMAIN, "add_purchase", service_data)
        else:
            await self.hass.services.async_call(DOMAIN, "add_burn", service_data)
