import logging
import async_timeout
import aiohttp
from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, API_BASE_URL

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=15)

class GranuloDataCoordinator(DataUpdateCoordinator):
    """Coordinateur de données Granulo utilisant la Cloud Function sécurisée."""
    
    def __init__(self, hass, user_id):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.user_id = user_id
        self.last_refresh = None

    async def _async_update_data(self):
        """Récupère les données agrégées et le statut Premium depuis Granulo."""
        url = f"{API_BASE_URL}/getHomeAssistantData"
        params = {"uid": self.user_id}

        try:
            async with async_timeout.timeout(30):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.last_refresh = datetime.now()
                            _LOGGER.debug("Granulo: Données reçues avec succès: %s", data)
                            return data
                        elif resp.status == 403:
                            err_data = await resp.json()
                            err_msg = err_data.get("error", "Compte non Premium")
                            _LOGGER.warning("Granulo: Accès refusé (403): %s", err_msg)
                            return {"error": "Abonnement Granulo+ requis"}
                        elif resp.status == 404:
                            _LOGGER.warning("Granulo: Utilisateur introuvable (404)")
                            return {"error": "Utilisateur non trouvé"}
                        else:
                            _LOGGER.error("Granulo: Erreur serveur %s", resp.status)
                            raise UpdateFailed(f"Erreur API Granulo: code {resp.status}")
        except Exception as e:
            _LOGGER.error("Granulo: Erreur de connexion au serveur Granulo: %s", e)
            raise UpdateFailed(f"Impossible de contacter Granulo: {e}")
