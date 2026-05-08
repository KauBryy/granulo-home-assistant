import logging
import voluptuous as vol
import aiohttp
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
from datetime import datetime
from .const import DOMAIN
from .coordinator import GranuloDataCoordinator

_LOGGER = logging.getLogger(__name__)

# Schéma pour les services
SERVICE_SCHEMA = vol.Schema({
    vol.Optional("amount", default=1.0): vol.Coerce(float),
    vol.Optional("note", default="Ajouté via Home Assistant"): cv.string,
    vol.Optional("price", default=0.0): vol.Coerce(float),
})

PROJECT_ID = "granulo-446e4"
API_KEY = "AIzaSyCmHG_" + "v4ymxmkNRiKc3" + "dU7PnIl_dV89u4c"

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
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "text", "button"])

    # 4. SERVICES
    async def handle_add_data(call: ServiceCall):
        amount = call.data.get("amount", 1.0)
        note = call.data.get("note", "Ajouté via Home Assistant")
        price = call.data.get("price", 0.0)
        
        # Vérification Premium
        settings_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/settings/{user_id}?key={API_KEY}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(settings_url) as resp:
                    if resp.status == 200:
                        s_data = await resp.json()
                        is_premium = s_data.get("fields", {}).get("isPremium", {}).get("booleanValue", False)
                        if not is_premium:
                            await _notify_error(hass, "Granulo Pro Requis", "Cette action est réservée aux abonnés Granulo+.")
                            return
                    else:
                        await _notify_error(hass, "Erreur Sync", "Impossible de vérifier votre statut Premium.")
                        return

            # Ajout Firebase
            collection = "bags" if "purchase" in call.service else "burns"
            url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection}?key={API_KEY}"
            
            payload = {
                "fields": {
                    "uid": {"stringValue": user_id},
                    "qty_sacks": {"doubleValue": float(amount)},
                    "date": {"timestampValue": datetime.utcnow().isoformat() + "Z"},
                    "note": {"stringValue": note}
                }
            }
            if collection == "bags":
                payload["fields"]["price_total"] = {"doubleValue": float(price)}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        # Forcer le rafraîchissement
                        await coordinator.async_refresh()
                        await _notify_success(hass, amount, "Achat" if collection == "bags" else "Brûlage")
                    else:
                        _LOGGER.error(f"Granulo: Erreur Firebase {response.status}")
        except Exception as e:
            _LOGGER.error(f"Granulo: Erreur: {e}")

    hass.services.async_register(DOMAIN, "add_burn", handle_add_data, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "add_purchase", handle_add_data, schema=SERVICE_SCHEMA)

    return True

async def _notify_error(hass, title, message):
    await hass.services.async_call("persistent_notification", "create", {"title": title, "message": message, "notification_id": "granulo_error"})

async def _notify_success(hass, amount, action):
    await hass.services.async_call("persistent_notification", "create", {
        "title": "Granulo Sync",
        "message": f"Commande envoyée : {amount} sac(s) ({action})",
        "notification_id": "granulo_sync"
    })

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Suppression de l'intégration Granulo."""
    hass.services.async_remove(DOMAIN, "add_burn")
    hass.services.async_remove(DOMAIN, "add_purchase")
    return await hass.config_entries.async_unload_platforms(entry, ["sensor", "number", "text", "button"])
