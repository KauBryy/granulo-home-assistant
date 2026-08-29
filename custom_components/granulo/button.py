import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    user_id = entry.data["user_id"]
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    
    entities = [
        GranuloActionButton(user_id, "burn", "Granulo Poele Enregistrer un Brulage", "mdi:fire"),
        GranuloActionButton(user_id, "purchase", "Granulo Poele Enregistrer un Achat", "mdi:cart")
    ]
    
    if coordinator:
        entities.append(GranuloRefreshButton(coordinator))
        
    async_add_entities(entities)

class GranuloRefreshButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "refresh_data"

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_icon = "mdi:refresh"
        self._attr_unique_id = f"granulo_refresh_v1_{coordinator.user_id}"
    
    @property
    def extra_state_attributes(self):
        return {
            "last_refresh": self.coordinator.last_refresh.isoformat() if self.coordinator.last_refresh else "Inconnu"
        }

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.user_id)},
            name="Granulo Poele",
            manufacturer="Granulo App",
            model="Expert Mode",
        )

    async def async_press(self) -> None:
        """Force le rafraîchissement des données."""
        await self.coordinator.async_refresh()

class GranuloActionButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, user_id, action_type, name, icon):
        self.user_id = user_id
        self.action_type = action_type
        self._attr_translation_key = f"{action_type}_action"
        self._attr_icon = icon
        self._attr_unique_id = f"granulo_btn_v1_{user_id}_{action_type}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.user_id)},
            name="Granulo Poele",
            manufacturer="Granulo App",
            model="Expert Mode",
        )

    async def async_press(self) -> None:
        """Appelé quand on appuie sur le bouton."""
        # 1. Récupérer les valeurs des inputs
        qty_entity = "number.granulo_poele_quantite"
        price_entity = "number.granulo_poele_prix"
        note_entity = "text.granulo_poele_note"

        qty = float(self.hass.states.get(qty_entity).state or 1.0) if self.hass.states.get(qty_entity) else 1.0
        price = float(self.hass.states.get(price_entity).state or 0.0) if self.hass.states.get(price_entity) else 0.0
        note = self.hass.states.get(note_entity).state if self.hass.states.get(note_entity) else "Ajouté via Home Assistant"

        # Marque sélectionnée
        brand = None
        for candidate_id in [
            "select.poele_granulo_marque_de_granules",
            "select.granulo_poele_marque",
            "select.poele_granulo_marque",
        ]:
            st = self.hass.states.get(candidate_id)
            if st and st.state and st.state not in ("unknown", "unavailable"):
                brand = st.state
                break

        if not brand:
            for s_id in self.hass.states.async_entity_ids("select"):
                if "granulo" in s_id or "marque" in s_id:
                    st = self.hass.states.get(s_id)
                    if st and st.state and st.state not in ("unknown", "unavailable"):
                        brand = st.state
                        break

        # 2. Appeler le service correspondant
        service_data = {"amount": qty, "note": note, "brand": brand}
        if self.action_type == "purchase":
            service_data["price"] = price
            await self.hass.services.async_call(DOMAIN, "add_purchase", service_data)
        else:
            await self.hass.services.async_call(DOMAIN, "add_burn", service_data)
