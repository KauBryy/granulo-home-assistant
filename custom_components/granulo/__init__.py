from homeassistant.core import HomeAssistant, Event
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuration de l'intégration Granulo."""
    hass.data.setdefault(DOMAIN, {})

    # On enregistre la plateforme sensor
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # On écoute l'événement 'granulo_update' (déclenché par l'app mobile via son API REST Events)
    async def handle_granulo_update(event: Event):
        # On diffuse les données instantanément à tous les capteurs Granulo de cet appareil
        async_dispatcher_send(hass, f"{DOMAIN}_update_{entry.entry_id}", event.data)

    # Enregistrement de l'écouteur pour qu'il soit détruit si l'intégration est supprimée
    entry.async_on_unload(
        hass.bus.async_listen("granulo_update", handle_granulo_update)
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Suppression de l'intégration Granulo."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

