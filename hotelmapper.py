from typing import Any, Dict, List, Union
import json


class TripjackToMMTHotelMapper:
    """
    Tripjack → MakeMyTrip (MMT) Hotel Metadata Mapper
    Produces exact MMT structure (metadata only, no pricing).
    """

    # ---------- Public API ----------
    def map(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns MMT-like response:
        {
          "response": {
            "personalizedSections": [
              {
                "hotels": [ ... ]
              }
            ]
          }
        }
        """
        hotels = self._extract_hotels(data)
        mapped_hotels = [self._map_hotel(h) for h in hotels]

        return {
            "response": {
                "personalizedSections": [
                    {
                        "hotels": mapped_hotels
                    }
                ]
            }
        }

    # ---------- Extraction ----------
    def _extract_hotels(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Supports:
        - Single hotel payload: { "hotel": {...} }
        - Search payload: { "searchResult": { "his": [...] } }
        """
        if "hotel" in data and isinstance(data["hotel"], dict):
            return [data["hotel"]]

        sr = data.get("searchResult", {})
        if isinstance(sr, dict) and isinstance(sr.get("his"), list):
            return [h for h in sr["his"] if isinstance(h, dict)]

        # Fallback: if data itself looks like a hotel
        if isinstance(data, dict) and data.get("name"):
            return [data]

        return []

    # ---------- Helpers ----------
    def _safe_float(self, v: Any) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def _to_media(self, hotel: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Normalize images to MMT:
        "media": [{ "url": "..." }, ...]
        """
        media: List[Dict[str, str]] = []

        imgs = hotel.get("imgs")
        if isinstance(imgs, list):
            for item in imgs:
                if isinstance(item, str):
                    media.append({"url": item})
                elif isinstance(item, dict):
                    url = item.get("url") or item.get("u")
                    if url:
                        media.append({"url": url})

        # Fallback to single image
        if not media:
            img = hotel.get("img")
            if isinstance(img, str) and img:
                media.append({"url": img})
            elif isinstance(img, dict):
                url = img.get("url") or img.get("u")
                if url:
                    media.append({"url": url})

        return media

    # ---------- Mapping ----------
    def _map_hotel(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map one Tripjack hotel → one MMT hotel object
        """
        ad = hotel.get("ad", {})
        city_name = (
            (ad.get("city") or {}).get("name")
            or ad.get("ctn")
            or ""
        )
        country_name = (ad.get("country") or {}).get("name") or ""

        gl = hotel.get("gl", {})
        lat = self._safe_float(gl.get("lt"))
        lng = self._safe_float(gl.get("ln"))

        return {
            "id": str(hotel.get("id", "")),
            "name": hotel.get("name", ""),
            "starRating": int(hotel.get("rt", 0)),

            # MMT location block
            "locationDetail": {
                "name": city_name,
                "countryName": country_name
            },

            # MMT geo block
            "geoLocation": {
                "latitude": lat,
                "longitude": lng
            },

            # MMT media block
            "media": self._to_media(hotel)
        }


# ---------- Local Test ----------
if __name__ == "__main__":
    try:
        with open("tripjack.json", "r") as f:
            data = json.load(f)

        mapper = TripjackToMMTHotelMapper()
        result = mapper.map(data)

        print("\n--- Mapped Hotels (first 1) ---\n")
        hotels = result["response"]["personalizedSections"][0]["hotels"]
        if hotels:
            print(json.dumps(hotels[0], indent=2))

        print(f"\nTotal hotels mapped: {len(hotels)}")

    except FileNotFoundError:
        print("Error: tripjackResponse.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")