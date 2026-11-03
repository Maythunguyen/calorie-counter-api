
from pathlib import Path
import json
import re
import pandas as pd
from openai import OpenAI

from app.helpers.load_env import load_env


CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "Food and Calories - Sheet1.csv"
)


class AiServices:
    def __init__(self, image_url: str):
        env = load_env()

        self.ai = OpenAI(api_key=env["openai_api_key"])
        self.image_url = image_url
        self.food_database = self._load_food_database()

    @staticmethod
    def _clean_cal(value) -> float:
        match = re.search(
            r"-?\d+(?:,\d{3})*(?:\.\d+)?",
            str(value)
        )

        if not match:
            raise ValueError(f"Invalid calorie value: {value}")

        return float(match.group(0).replace(",", ""))

    def _load_food_database(self) -> dict:
        df = pd.read_csv(CSV_PATH)

        required = {"Food", "Serving", "Calories"}
        if not required.issubset(df.columns):
            raise ValueError("Invalid food CSV columns")

        food_database = {}

        for row in df.itertuples(index=False):
            food_name = str(row.Food).strip().lower()
            serving = str(row.Serving).strip().lower()

            if serving != "100 g":
                raise ValueError(
                    f"{food_name}: expected 100 g, got {serving}"
                )

            calories = self._clean_cal(row.Calories)

            if not 0 <= calories <= 900:
                raise ValueError(
                    f"Invalid calories for {food_name}: {calories}"
                )

            if (
                food_name in food_database
                and food_database[food_name] != calories
            ):
                raise ValueError(
                    f"Conflicting calories for: {food_name}"
                )

            food_database[food_name] = calories

        return food_database

    def _build_food_prompt(self) -> str:
        return "\n".join(
            f"{name}: {calories:g} kcal per 100 g"
            for name, calories in self.food_database.items()
        )

    def image_analysis(self) -> dict:
        system_msg = f"""
            You are a food-image recognition assistant.

            Your job is to identify visible foods in an image
            and estimate the edible weight of each item in grams.

            FOOD DATABASE:
            {self._build_food_prompt()}

            RULES:
            1. Identify each visible food component separately.
            2. Match foods to exact names from the database.
            3. Return the database food name exactly as written.
            4. Estimate the edible portion in grams.
            5. Consider whether the food is cooked or raw.
            6. Do not include plates, bones or packaging in weight.
            7. Include visible sauces, toppings and cooking oils
            when you can reasonably identify them.
            8. Do not invent exact quantities.
            9. If a food cannot be matched, set food_name to null.
            10. Return at most 12 food components.
            11. Do not calculate calories.
            12. Only return valid JSON.

            Remember: food weights estimated from an image
            are approximate, not measurements.
            """

        response = self.ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Identify the foods and estimate "
                                "their edible weights in grams."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": self.image_url,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "food_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "food_name": {
                                            "type": ["string", "null"]
                                        },
                                        "estimated_grams": {
                                            "type": "number"
                                        }
                                    },
                                    "required": [
                                        "food_name",
                                        "estimated_grams"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["items"],
                        "additionalProperties": False
                    }
                }
            },
            max_tokens=600
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("AI returned an empty response")

        analysis = json.loads(content)

        food_items = []
        calories_per_item = []
        estimated_grams = []
        unmatched_items = []

        for item in analysis["items"][:12]:
            name = item["food_name"]
            grams = float(item["estimated_grams"])

            if not 0 < grams <= 2000:
                continue

            if not isinstance(name, str):
                unmatched_items.append("Unknown food")
                continue

            name = name.strip().lower()

            if name not in self.food_database:
                unmatched_items.append(name)
                continue

            calories_per_100g = self.food_database[name]

            calories = grams * calories_per_100g / 100

            food_items.append(name)
            estimated_grams.append(round(grams, 1))
            calories_per_item.append(round(calories, 1))

        total_calories = round(sum(calories_per_item), 1)

        return {
            "food_items": food_items,
            "estimated_grams": estimated_grams,
            "calories_per_item": calories_per_item,
            "total_calories": total_calories,
            "unmatched_items": unmatched_items,
            "is_estimate": True
        }


if __name__ == "__main__":
    img = (
        "https://static01.nyt.com/images/2024/01/05/"
        "multimedia/ND-Poke-bowl-bfwm/"
        "ND-Poke-bowl-bfwm-superJumbo.jpg"
    )

    service = AiServices(img)
    result = service.image_analysis()

    print(json.dumps(result, indent=2))
