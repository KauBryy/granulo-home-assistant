import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class GranuloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de config pour Granulo."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Étape initiale quand l'utilisateur ajoute l'intégration."""
        errors = {}
        if user_input is not None:
            if not user_input.get("user_id"):
                errors["base"] = "user_id_missing"
            else:
                return self.async_create_entry(title="Mon Assistant Granulo", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("user_id"): str,
            }),
            errors=errors,
        )
