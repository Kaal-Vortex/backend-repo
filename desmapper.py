from typing import Any, Dict, List
import json


class TripjackDescriptionMapper:
    """
    Converts Tripjack 'des' field into structured sections
    """

    def map(self, hotel: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        raw_des = hotel.get("des")

        if not raw_des or not isinstance(raw_des, str):
            return {"descriptionSections": []}

        parsed = self._safe_parse(raw_des)
        if not parsed:
            return {"descriptionSections": []}

        sections = []

        for key, value in parsed.items():
            if not value:
                continue

            sections.append({
                "title": self._format_title(key),
                "content": value.strip()
            })

        return {"descriptionSections": sections}

    # ---------- Helpers ----------

    def _safe_parse(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _format_title(self, key: str) -> str:
        return key.replace("_", " ").title()


# =========================================================
# FUNCTION WRAPPER (FOR USING THE FUNCTION INSTED OF CLASS)
# =========================================================

def map_tripjack_description(hotel: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Functional interface for Django usage
    """
    mapper = TripjackDescriptionMapper()
    return mapper.map(hotel)


# =========================================================
# ---------- Local Test ----------
# =========================================================

if __name__ == "__main__":
    try:
        with open("tripjack.json", "r") as f:
            data = json.load(f)

        hotel = data.get("hotel", {})

        result = map_tripjack_description(hotel)

        print("\n--- Description Sections ---\n")
        for section in result["descriptionSections"]:
            print(f"{section['title']}:")
            print(section["content"][:120], "...\n")

        print(f"Total sections: {len(result['descriptionSections'])}")

    except Exception as e:
        print("Error:", str(e))

##################################################################################

# from typing import Any, Dict, List
# import json


# class TripjackDescriptionMapper:
#     """
#     Converts Tripjack 'des' field into structured sections
#     """

#     def map(self, hotel: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
#         raw_des = hotel.get("des")

#         if not raw_des or not isinstance(raw_des, str):
#             return {"descriptionSections": []}

#         parsed = self._safe_parse(raw_des)
#         if not parsed:
#             return {"descriptionSections": []}

#         sections = []

#         for key, value in parsed.items():
#             if not value:
#                 continue

#             sections.append({
#                 "title": self._format_title(key),
#                 "content": value.strip()
#             })

#         return {"descriptionSections": sections}

#     # ---------- Helpers ----------

#     def _safe_parse(self, raw: str) -> Dict[str, Any]:
#         try:
#             return json.loads(raw)
#         except (json.JSONDecodeError, TypeError):
#             return {}

#     def _format_title(self, key: str) -> str:
#         """
#         Convert:
#         'spoken_languages' → 'Spoken Languages'
#         """
#         return key.replace("_", " ").title()


# # ---------- Local Test ----------
# if __name__ == "__main__":
#     try:
#         with open("tripjack.json", "r") as f:
#             data = json.load(f)

#         hotel = data.get("hotel", {})

#         mapper = TripjackDescriptionMapper()
#         result = mapper.map(hotel)

#         print("\n--- Description Sections ---\n")
#         for section in result["descriptionSections"]:
#             print(f"{section['title']}:")
#             print(section["content"][:120], "...\n")

#         print(f"Total sections: {len(result['descriptionSections'])}")

#     except Exception as e:
#         print("Error:", str(e))