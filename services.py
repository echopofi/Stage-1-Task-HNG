import httpx
import asyncio


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
            
        except httpx.RequestError:
            return "External API", None

        gen_data, agi_data, nat_data = [r.json() for r in responses]

        if not gen_data.get("gender") or gen_data.get("count") == 0:
            return "Genderize", None
        
        if agi_data.get("age") is None:
            return "Agify", None
        
        if not nat_data.get("country"):
            return "Nationalize", None
        
        top_country = max(nat_data["country"], key=lambda x: x["probability"])

        return None, {
            "gender": gen_data["gender"],
            "gender_probability": gen_data["probability"],
            "sample_size": gen_data["count"],
            "age": agi_data["age"],
            "age_group": get_age_group(agi_data["age"]),
            "country_id": top_country["country_id"],
            "country_probability": top_country["probability"],
        }