# app/services/ai_service.py
from pathlib import Path
import re
import pandas as pd
from openai import OpenAI
from app.helpers.load_env import load_env

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "Food and Calories - Sheet1.csv"
env = load_env()
print("🔑 OpenAI Key:", env["openai_api_key"]) 

class AiServices:
    def __init__(self, image_url: str):
        self.ai = OpenAI(api_key=env["openai_api_key"])
        self.image_url  = image_url
        self.food_prompt = self._build_food_prompt()

    @staticmethod
    def _clean_cal(value: str) -> int:
        m = re.search(r"\d+(?:,\d+)?", str(value))
        return int(m.group(0).replace(",", "")) if m else 0

    def _build_food_prompt(self) -> str:
        df = pd.read_csv(CSV_PATH)
        df.columns = ["Food", "Serving", "Calories"]
        df["Food"] = df["Food"].str.lower().str.strip()
        df["Calories"] = df["Calories"].apply(self._clean_cal)
        rows = [f"{r.Food} – {r.Calories} kcal" for r in df.itertuples(index=False)]
        return "\n".join(rows)

    def image_analysis(self) -> dict:
        system_msg = (
            "You are a food-image assistant.\n\n"
            "Below is a list of foods with average calories:\n"
            f"{self.food_prompt}\n\n"
            "Return **only** JSON like:\n"
            '{ "food_items": ["item1"], "calories_per_item": [123], "total_calories": 123 }'
        )

        messages = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",          # <- correct
                        "image_url": {"url": self.image_url}
                    }
                ],
            },
        ]

        rsp = self.ai.chat.completions.create(
            model="gpt-4o-mini",              
            messages=messages,
            max_tokens=400,
            temperature=0.2,
        )

        return rsp.choices[0].message.content

if __name__ == "__main__":
    img = "https://static01.nyt.com/images/2024/01/05/multimedia/ND-Poke-bowl-bfwm/ND-Poke-bowl-bfwm-superJumbo.jpg"
    svc = AiServices(img)
    print(svc.image_analysis())
