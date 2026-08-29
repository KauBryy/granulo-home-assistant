import logging
import voluptuous as vol
import aiohttp
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, API_BASE_URL
from .coordinator import GranuloDataCoordinator

_LOGGER = logging.getLogger(__name__)

# Schéma pour les services
SERVICE_SCHEMA = vol.Schema({
    vol.Optional("amount", default=1.0): vol.Coerce(float),
    vol.Optional("note", default="Ajouté via Home Assistant"): cv.string,
    vol.Optional("price", default=0.0): vol.Coerce(float),
    vol.Optional("brand"): cv.string,
})

PLATFORMS = ["sensor", "number", "text", "button", "select"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration de l'intégration Granulo."""
    hass.data.setdefault(DOMAIN, {})
    user_id = entry.data.get("user_id")

    # 1. Créer le coordinateur central
    coordinator = GranuloDataCoordinator(hass, user_id)
    await coordinator.async_config_entry_first_refresh()
    
    # 2. Le stocker pour toutes les plateformes
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # 3. Enregistrer les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 4. SERVICES
    async def handle_add_data(call: ServiceCall):
        amount = call.data.get("amount", 1.0)
        note = call.data.get("note", "Ajouté via Home Assistant")
        price = call.data.get("price", 0.0)
        brand = call.data.get("brand")
        action = "purchase" if "purchase" in call.service else "burn"

        url = f"{API_BASE_URL}/homeAssistantAction"
        payload = {
            "uid": user_id,
            "action": action,
            "amount": amount,
            "price": price,
            "note": note,
            "brand": brand,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        await coordinator.async_refresh()
                        action_label = "Achat" if action == "purchase" else "Brûlage"
                        brand_label = f" ({brand})" if brand and brand != "Générique" else ""
                        await _notify_success(hass, amount, f"{action_label}{brand_label}")
                    elif response.status == 403:
                        await _notify_error(hass, "Granulo Pro Requis", "Cette action est réservée aux abonnés Granulo+.")
                    else:
                        resp_data = await response.json()
                        err_msg = resp_data.get("error", f"Erreur {response.status}")
                        await _notify_error(hass, "Erreur Sync Granulo", err_msg)
        except Exception as e:
            _LOGGER.error("Granulo: Erreur lors de l'appel Cloud Function: %s", e)
            await _notify_error(hass, "Erreur Réseau", f"Impossible de contacter le serveur Granulo: {e}")

    hass.services.async_register(DOMAIN, "add_burn", handle_add_data, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "add_purchase", handle_add_data, schema=SERVICE_SCHEMA)

    return True

async def _notify_error(hass, title, message):
    await hass.services.async_call("persistent_notification", "create", {"title": title, "message": message, "notification_id": "granulo_error"})

async def _notify_success(hass, amount, action):
    await hass.services.async_call("persistent_notification", "create", {
        "title": "Granulo Sync",
        "message": f"Commande envoyée : {amount} sac(s) {action}",
        "notification_id": "granulo_sync"
    })

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Suppression de l'intégration Granulo."""
    hass.services.async_remove(DOMAIN, "add_burn")
    hass.services.async_remove(DOMAIN, "add_purchase")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
