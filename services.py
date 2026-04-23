import httpx
import asyncio
from models import COUNTRY_MAP


def get_age_group(age:int) -> str:
    if age <= 12: 
        return "child"
    elif age <= 19: 
        return "teenager"
    elif age <= 59: 
        return "adult"
    else: 
        return "senior"
    
async def fetch_profile_data(name: str):
    urls = {
        "Genderize": f"https://api.genderize.io?name={name}",
        "Agify": f"https://api.agify.io?name={name}",
        "Nationalize": f"https://api.nationalize.io?name={name}"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:    
            responses = await asyncio.gather(
                client.get(urls["Genderize"]),
                client.get(urls["Agify"]),
                client.get(urls["Nationalize"])
            )
        except (httpx.RequestError, httpx.TimeoutException):
            return "External API", None

        gen_data = responses[0].json()
        agi_data = responses[1].json()
        nat_data = responses[2].json()

        if not gen_data.get("gender") or gen_data.get("count") == 0:
            return "Genderize", None
        
        if agi_data.get("age") is None:
            return "Agify", None
        
        if not nat_data.get("country"):
            return "Nationalize", None
        
        top_country = max(nat_data["country"], key=lambda x: x["probability"])
        country_id = top_country["country_id"]
        country_name = COUNTRY_MAP.get(country_id, country_id)

        return None, {
            "gender": gen_data["gender"],
            "gender_probability": gen_data["probability"],
            "sample_size": gen_data["count"],
            "age": agi_data["age"],
            "age_group": get_age_group(agi_data["age"]),
            "country_id": country_id,
            "country_name": country_name,
            "country_probability": top_country["probability"],
        }