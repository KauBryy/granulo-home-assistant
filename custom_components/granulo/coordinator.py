import logging
import async_timeout
import aiohttp
from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=360)
PROJECT_ID = "granulo-446e4"
API_KEY = "AIzaSyCmHG_" + "v4ymxmkNRiKc3" + "dU7PnIl_dV89u4c"

class GranuloDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, user_id):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.user_id = user_id
        self.last_refresh = None

    async def _fetch_all_documents(self, session, collection):
        """Récupère tous les documents pour faire les calculs en mémoire (comme l'app Flutter)."""
        url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents:runQuery?key={API_KEY}"
        
        query = {
            "structuredQuery": {
                "from": [{"collectionId": collection}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "uid"},
                        "op": "EQUAL",
                        "value": {"stringValue": self.user_id}
                    }
                }
            }
        }

        async with session.post(url, json=query) as resp:
            if resp.status != 200: return []
            res = await resp.json()
            docs = []
            for item in res:
                doc = item.get("document")
                if doc:
                    fields = doc.get("fields", {})
                    date_str = fields.get("date", {}).get("timestampValue")
                    qty = float(fields.get("qty_sacks", {}).get("doubleValue", 0.0) or fields.get("qty_sacks", {}).get("integerValue", 0.0))
                    cost = float(fields.get("price_total", {}).get("doubleValue", 0.0) or fields.get("price_total", {}).get("integerValue", 0.0))
                    if date_str:
                        dt = datetime.fromisoformat(date_str.replace("Z", ""))
                        docs.append({"date": dt, "qty": qty, "cost": cost})
            return docs

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(45):
                async with aiohttp.ClientSession() as session:
                    # 1. Get Settings
                    settings_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/settings/{self.user_id}?key={API_KEY}"
                    initial_stock_sacks = 0.0
                    default_weight = 15.0
                    season_start_month = 8
                    last_glass_dt = None
                    last_maint_dt = None
                    async with session.get(settings_url) as resp:
                        if resp.status == 200:
                            s_data = await resp.json()
                            fields = s_data.get("fields", {})
                            default_weight = float(fields.get("defaultWeightKg", {}).get("doubleValue", 15.0) or fields.get("defaultWeightKg", {}).get("integerValue", 15.0))
                            season_start_month = int(fields.get("seasonStartMonth", {}).get("integerValue", 8) or fields.get("seasonStartMonth", {}).get("doubleValue", 8))
                            last_glass = fields.get("lastGlassCleanDate", {}).get("timestampValue")
                            last_maint = fields.get("lastRegularMaintenanceDate", {}).get("timestampValue")
                            if last_glass: last_glass_dt = datetime.fromisoformat(last_glass.replace("Z", ""))
                            if last_maint: last_maint_dt = datetime.fromisoformat(last_maint.replace("Z", ""))
                            init_stock_map = fields.get("initialStockByType", {}).get("mapValue", {}).get("fields", {})
                            for k, v in init_stock_map.items():
                                initial_stock_sacks += float(v.get("doubleValue", 0.0) or v.get("integerValue", 0.0))
                            
                            is_premium = fields.get("isPremium", {}).get("booleanValue", False)
                            if not is_premium:
                                _LOGGER.warning(f"Granulo: L'utilisateur {self.user_id} n'est pas Premium. Accès refusé.")
                                return {"error": "Premium Requis", "is_premium": False}

                    # 2. Fetch all data
                    all_purchases = await self._fetch_all_documents(session, "bags")
                    all_burns = await self._fetch_all_documents(session, "burns")

                    # 3. Dates
                    now = datetime.utcnow()
                    if now.month >= season_start_month:
                        season_start = datetime(now.year, season_start_month, 1)
                    else:
                        season_start = datetime(now.year - 1, season_start_month, 1)
                    
                    week_ago = now - timedelta(days=7)
                    twenty_days_ago = now - timedelta(days=20)
                    month_start = datetime(now.year, now.month, 1)

                    # 4. Aggregations
                    def sum_docs(docs, start_dt=None, end_dt=None):
                        q = 0.0; c = 0.0
                        for d in docs:
                            if start_dt and d["date"] < start_dt: continue
                            if end_dt and d["date"] > end_dt: continue
                            q += d["qty"]; c += d["cost"]
                        return {"qty": q, "cost": c}

                    all_p = sum_docs(all_purchases)
                    all_b = sum_docs(all_burns)
                    season_p = sum_docs(all_purchases, start_dt=season_start)
                    season_b = sum_docs(all_burns, start_dt=season_start)
                    week_b = sum_docs(all_burns, start_dt=week_ago)
                    twenty_b = sum_docs(all_burns, start_dt=twenty_days_ago)
                    month_b = sum_docs(all_burns, start_dt=month_start)
                    
                    glass_b = sum_docs(all_burns, start_dt=last_glass_dt) if last_glass_dt else {"qty": 0.0}
                    maint_b = sum_docs(all_burns, start_dt=last_maint_dt) if last_maint_dt else {"qty": 0.0}

                    # 5. Calculations
                    stock_sacks = initial_stock_sacks + all_p["qty"] - all_b["qty"]
                    days_in_season = max(1, (now - season_start).days)
                    conso_quotidienne_20j = twenty_b["qty"] / 20.0
                    
                    data = {
                        "stock_actuel": round(stock_sacks, 1),
                        "stock_kg": round(stock_sacks * default_weight, 1),
                        "achats_saison": round(season_p["qty"], 1),
                        "brulages_saison": round(season_b["qty"], 1),
                        "achats_total": round(all_p["qty"], 1),
                        "brulages_total": round(all_b["qty"], 1),
                        "depenses_saison": round(season_p["cost"], 2),
                        "depenses_total": round(all_p["cost"], 2),
                        "moyenne_7j": round((week_b["qty"] * default_weight) / 7.0, 1),
                        "moyenne_mois": round((month_b["qty"] * default_weight) / now.day, 1),
                        "moyenne_saison": round((season_b["qty"] * default_weight) / days_in_season, 1),
                        "jours_restants": round(stock_sacks / conso_quotidienne_20j, 1) if conso_quotidienne_20j > 0 else stock_sacks * 2,
                        "vitre": round(glass_b["qty"], 1),
                        "entretien": round(maint_b["qty"], 1)
                    }
                    self.last_refresh = datetime.utcnow()
                    return data
        except Exception as e:
            _LOGGER.error(f"Erreur Granulo Update: {e}")
            raise UpdateFailed(f"Error communicating with API: {e}")
