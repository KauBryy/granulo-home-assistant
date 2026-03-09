import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class GranuloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de config pour Granulo."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Étape initiale quand l'utilisateur ajoute l'intégration."""
        errors = {}
        if user_input is not None:
            # Pour l'instant on valide juste qu'il y a un nom
            return self.async_create_entry(title="Mon Assistant Granulo", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default="Granulo"): str,
            }),
            errors=errors,
        )
