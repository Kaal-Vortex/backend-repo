from typing import Any, Dict, List
import json


# ==============================
# 1. PRICE MAPPER (UNCHANGED)
# ==============================
class TripjackToMMTPriceMapper:

    def __init__(self, pricing_key: str = "DEFAULT"):
        self.pricing_key = pricing_key

    def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        hotel = data.get("hotel", data)

        price_units = self._extract_rooms(hotel)
        return [self._map_price_detail(unit) for unit in price_units]

    def _extract_rooms(self, hotel: Dict[str, Any]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for op in hotel.get("ops", []):
            if not isinstance(op, dict):
                continue

            for room in op.get("ris", []):
                if not isinstance(room, dict):
                    continue

                results.append({
                    "tp": room.get("tp"),
                    "tfcs": room.get("tfcs", {}),
                    "tafcs": room.get("tafcs", {}),
                    "rate_id": room.get("id", "")
                })

        return results

    def _safe_float(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    def _map_price_detail(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        tp = self._safe_float(unit.get("tp"))

        tfcs = unit.get("tfcs", {})
        tafcs = unit.get("tafcs", {}).get("TAF", {})

        display_price = self._safe_float(tfcs.get("BF"))
        tax = self._safe_float(tfcs.get("TAF"))
        final_price = tp or self._safe_float(tfcs.get("TF"))

        strike_price = self._safe_float(tafcs.get("SBP"))

        if display_price == 0:
            display_price = final_price - tax

        if strike_price == 0:
            strike_price = display_price

        return {
            "priceDetail": {
                "displayPrice": round(display_price, 2),
                "price": round(strike_price, 2),
                "priceWithTax": round(final_price, 2),

                "discountedPrice": round(display_price, 2),
                "discountedPriceWithTax": round(final_price, 2),

                "totalTax": round(tax, 2),

                "pricingKey": self.pricing_key,
                "ratePlanCode": str(unit.get("rate_id", "")),

                "discountedPriceWithTaxAndFees": round(final_price, 2),
                "totalTaxWithFees": round(tax, 2),
                "totalAdditionalFees": 0.0,
            }
        }


# FUNCTION WRAPPER
def map_tripjack_price(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    mapper = TripjackToMMTPriceMapper()
    return mapper.map(data)


# ==============================
# 2. HOTEL MAPPER (UNCHANGED)
# ==============================
class TripjackToMMTHotelMapper:

    def map(self, data: Dict[str, Any]) -> Dict[str, Any]:
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

    def _extract_hotels(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if "hotel" in data and isinstance(data["hotel"], dict):
            return [data["hotel"]]

        sr = data.get("searchResult", {})
        if isinstance(sr, dict) and isinstance(sr.get("his"), list):
            return [h for h in sr["his"] if isinstance(h, dict)]

        if isinstance(data, dict) and data.get("name"):
            return [data]

        return []

    def _safe_float(self, v: Any) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def _to_media(self, hotel: Dict[str, Any]) -> List[Dict[str, str]]:
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

        if not media:
            img = hotel.get("img")
            if isinstance(img, str) and img:
                media.append({"url": img})
            elif isinstance(img, dict):
                url = img.get("url") or img.get("u")
                if url:
                    media.append({"url": url})

        return media

    def _map_hotel(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
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

            "locationDetail": {
                "name": city_name,
                "countryName": country_name
            },

            "geoLocation": {
                "latitude": lat,
                "longitude": lng
            },

            "media": self._to_media(hotel)
        }


# FUNCTION WRAPPER
def map_tripjack_hotel(data: Dict[str, Any]) -> Dict[str, Any]:
    mapper = TripjackToMMTHotelMapper()
    return mapper.map(data)


# ==============================
# 3. DESCRIPTION MAPPER (UNCHANGED)
# ==============================
class TripjackDescriptionMapper:

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

    def _safe_parse(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _format_title(self, key: str) -> str:
        return key.replace("_", " ").title()


# FUNCTION WRAPPER
def map_tripjack_description(hotel: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    mapper = TripjackDescriptionMapper()
    return mapper.map(hotel)


# ==============================
# AGGREGATOR (UNCHANGED)
# ==============================
class TripjackMapper:

    def __init__(self):
        self.hotel_mapper = TripjackToMMTHotelMapper()
        self.price_mapper = TripjackToMMTPriceMapper()
        self.desc_mapper = TripjackDescriptionMapper()

    def map(self, data: Dict[str, Any]) -> Dict[str, Any]:

        hotel_response = self.hotel_mapper.map(data)

        hotels = hotel_response.get("response", {}) \
                                .get("personalizedSections", [{}])[0] \
                                .get("hotels", [])

        if not hotels:
            return hotel_response

        hotel = hotels[0]

        raw_hotel = data.get("hotel", data)

        price_data = self.price_mapper.map(data)
        if not isinstance(price_data, list):
            price_data = [price_data]

        rooms = []
        for price in price_data:
            rooms.append({
                "priceDetail": price.get("priceDetail", {})
            })

        desc_data = self.desc_mapper.map(raw_hotel)

        hotel["rooms"] = rooms
        hotel["descriptionSections"] = desc_data.get("descriptionSections", [])

        return hotel_response


# FUNCTION WRAPPER (MAIN ENTRY)
def map_tripjack(data: Dict[str, Any]) -> Dict[str, Any]:
    mapper = TripjackMapper()
    return mapper.map(data)


# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    try:
        with open("tripjack.json", "r") as f:
            data = json.load(f)

        result = map_tripjack(data)

        with open("mapped_output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print("\n Output saved to mapped_output.json")

    except Exception as e:
        print("Error:", str(e))

##################################################################################

# from typing import Any, Dict, List
# import json


# # ==============================
# # PRICE MAPPER (UNCHANGED)
# # ==============================
# class TripjackToMMTPriceMapper:
#     """
#     Final production mapper:
#     Tripjack → MakeMyTrip priceDetail (UI-aligned)
#     """

#     def __init__(self, pricing_key: str = "DEFAULT"):
#         self.pricing_key = pricing_key

#     def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         hotel = data.get("hotel", data)

#         price_units = self._extract_rooms(hotel)
#         return [self._map_price_detail(unit) for unit in price_units]

#     def _extract_rooms(self, hotel: Dict[str, Any]) -> List[Dict[str, Any]]:
#         results: List[Dict[str, Any]] = []

#         for op in hotel.get("ops", []):
#             if not isinstance(op, dict):
#                 continue

#             for room in op.get("ris", []):
#                 if not isinstance(room, dict):
#                     continue

#                 results.append({
#                     "tp": room.get("tp"),
#                     "tfcs": room.get("tfcs", {}),
#                     "tafcs": room.get("tafcs", {}),
#                     "rate_id": room.get("id", "")
#                 })

#         return results

#     def _safe_float(self, value: Any) -> float:
#         if isinstance(value, (int, float)):
#             return float(value)
#         if isinstance(value, str):
#             try:
#                 return float(value)
#             except ValueError:
#                 return 0.0
#         return 0.0

#     def _map_price_detail(self, unit: Dict[str, Any]) -> Dict[str, Any]:
#         tp = self._safe_float(unit.get("tp"))

#         tfcs = unit.get("tfcs", {})
#         tafcs = unit.get("tafcs", {}).get("TAF", {})

#         display_price = self._safe_float(tfcs.get("BF"))
#         tax = self._safe_float(tfcs.get("TAF"))
#         final_price = tp or self._safe_float(tfcs.get("TF"))

#         strike_price = self._safe_float(tafcs.get("SBP"))

#         if display_price == 0:
#             display_price = final_price - tax

#         if strike_price == 0:
#             strike_price = display_price

#         return {
#             "priceDetail": {
#                 "displayPrice": round(display_price, 2),
#                 "price": round(strike_price, 2),
#                 "priceWithTax": round(final_price, 2),

#                 "discountedPrice": round(display_price, 2),
#                 "discountedPriceWithTax": round(final_price, 2),

#                 "totalTax": round(tax, 2),

#                 "pricingKey": self.pricing_key,
#                 "ratePlanCode": str(unit.get("rate_id", "")),

#                 "discountedPriceWithTaxAndFees": round(final_price, 2),
#                 "totalTaxWithFees": round(tax, 2),
#                 "totalAdditionalFees": 0.0,
#             }
#         }


# # ==============================
# # HOTEL MAPPER (UNCHANGED)
# # ==============================
# class TripjackToMMTHotelMapper:

#     def map(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         hotels = self._extract_hotels(data)
#         mapped_hotels = [self._map_hotel(h) for h in hotels]

#         return {
#             "response": {
#                 "personalizedSections": [
#                     {
#                         "hotels": mapped_hotels
#                     }
#                 ]
#             }
#         }

#     def _extract_hotels(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         if "hotel" in data and isinstance(data["hotel"], dict):
#             return [data["hotel"]]

#         sr = data.get("searchResult", {})
#         if isinstance(sr, dict) and isinstance(sr.get("his"), list):
#             return [h for h in sr["his"] if isinstance(h, dict)]

#         if isinstance(data, dict) and data.get("name"):
#             return [data]

#         return []

#     def _safe_float(self, v: Any) -> float:
#         try:
#             return float(v)
#         except (TypeError, ValueError):
#             return 0.0

#     def _to_media(self, hotel: Dict[str, Any]) -> List[Dict[str, str]]:
#         media: List[Dict[str, str]] = []

#         imgs = hotel.get("imgs")
#         if isinstance(imgs, list):
#             for item in imgs:
#                 if isinstance(item, str):
#                     media.append({"url": item})
#                 elif isinstance(item, dict):
#                     url = item.get("url") or item.get("u")
#                     if url:
#                         media.append({"url": url})

#         if not media:
#             img = hotel.get("img")
#             if isinstance(img, str) and img:
#                 media.append({"url": img})
#             elif isinstance(img, dict):
#                 url = img.get("url") or img.get("u")
#                 if url:
#                     media.append({"url": url})

#         return media

#     def _map_hotel(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
#         ad = hotel.get("ad", {})
#         city_name = (
#             (ad.get("city") or {}).get("name")
#             or ad.get("ctn")
#             or ""
#         )
#         country_name = (ad.get("country") or {}).get("name") or ""

#         gl = hotel.get("gl", {})
#         lat = self._safe_float(gl.get("lt"))
#         lng = self._safe_float(gl.get("ln"))

#         return {
#             "id": str(hotel.get("id", "")),
#             "name": hotel.get("name", ""),
#             "starRating": int(hotel.get("rt", 0)),

#             "locationDetail": {
#                 "name": city_name,
#                 "countryName": country_name
#             },

#             "geoLocation": {
#                 "latitude": lat,
#                 "longitude": lng
#             },

#             "media": self._to_media(hotel)
#         }


# # ==============================
# # DESCRIPTION MAPPER (UNCHANGED)
# # ==============================
# class TripjackDescriptionMapper:

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

#     def _safe_parse(self, raw: str) -> Dict[str, Any]:
#         try:
#             return json.loads(raw)
#         except (json.JSONDecodeError, TypeError):
#             return {}

#     def _format_title(self, key: str) -> str:
#         return key.replace("_", " ").title()


# # ==============================
# # AGGREGATOR (NEW)
# # ==============================
# class TripjackMapper:

#     def __init__(self):
#         self.hotel_mapper = TripjackToMMTHotelMapper()
#         self.price_mapper = TripjackToMMTPriceMapper()
#         self.desc_mapper = TripjackDescriptionMapper()

#     def map(self, data: Dict[str, Any]) -> Dict[str, Any]:

#         # Step 1: Hotel base structure
#         hotel_response = self.hotel_mapper.map(data)

#         hotels = hotel_response.get("response", {}) \
#                                 .get("personalizedSections", [{}])[0] \
#                                 .get("hotels", [])

#         if not hotels:
#             return hotel_response

#         hotel = hotels[0]

#         # Step 2: Raw hotel
#         raw_hotel = data.get("hotel", data)

#         # Step 3: Price
#         price_data = self.price_mapper.map(data)
#         if not isinstance(price_data, list):
#             price_data = [price_data]

#         rooms = []
#         for price in price_data:
#             rooms.append({
#                 "priceDetail": price.get("priceDetail", {})
#             })

#         # Step 4: Description
#         desc_data = self.desc_mapper.map(raw_hotel)

#         # Step 5: Inject
#         hotel["rooms"] = rooms
#         hotel["descriptionSections"] = desc_data.get("descriptionSections", [])

#         return hotel_response


# # ==============================
# # TEST
# # ==============================
# if __name__ == "__main__":
#     try:
#         with open("tripjack.json", "r") as f:
#             data = json.load(f)

#         mapper = TripjackMapper()
#         result = mapper.map(data)

#         # ---------- SAVE OUTPUT ----------
#         output_file = "mapped_output.json"

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(result, f, indent=2, ensure_ascii=False)

#         print(f"\n✅ Output saved to: {output_file}")

#     except Exception as e:
#         print("Error:", str(e))

##################################################################################################
#some minimal changes and improvments

# from typing import Any, Dict, List
# import json


# # =========================================================
# # Shared Utilities (centralized, no logic change)
# # =========================================================

# class _Utils:

#     @staticmethod
#     def safe_float(value: Any) -> float:
#         if isinstance(value, (int, float)):
#             return float(value)
#         if isinstance(value, str):
#             try:
#                 return float(value)
#             except ValueError:
#                 return 0.0
#         return 0.0


# # =========================================================
# # Price Mapper (LOGIC PRESERVED)
# # =========================================================

# class PriceMapper:

#     def __init__(self, pricing_key: str = "DEFAULT"):
#         self.pricing_key = pricing_key

#     def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         hotel = data.get("hotel", data)
#         price_units = self._extract_rooms(hotel)
#         return [self._map_price_detail(unit) for unit in price_units]

#     def _extract_rooms(self, hotel: Dict[str, Any]) -> List[Dict[str, Any]]:
#         results: List[Dict[str, Any]] = []

#         for op in hotel.get("ops", []):
#             if not isinstance(op, dict):
#                 continue

#             for room in op.get("ris", []):
#                 if not isinstance(room, dict):
#                     continue

#                 results.append({
#                     "tp": room.get("tp"),
#                     "tfcs": room.get("tfcs", {}),
#                     "tafcs": room.get("tafcs", {}),
#                     "rate_id": room.get("id", "")
#                 })

#         return results

#     def _map_price_detail(self, unit: Dict[str, Any]) -> Dict[str, Any]:
#         tp = _Utils.safe_float(unit.get("tp"))

#         tfcs = unit.get("tfcs", {})
#         tafcs = unit.get("tafcs", {}).get("TAF", {})

#         display_price = _Utils.safe_float(tfcs.get("BF"))
#         tax = _Utils.safe_float(tfcs.get("TAF"))
#         final_price = tp or _Utils.safe_float(tfcs.get("TF"))

#         strike_price = _Utils.safe_float(tafcs.get("SBP"))

#         if display_price == 0:
#             display_price = final_price - tax

#         if strike_price == 0:
#             strike_price = display_price

#         return {
#             "priceDetail": {
#                 "displayPrice": round(display_price, 2),
#                 "price": round(strike_price, 2),
#                 "priceWithTax": round(final_price, 2),

#                 "discountedPrice": round(display_price, 2),
#                 "discountedPriceWithTax": round(final_price, 2),

#                 "totalTax": round(tax, 2),

#                 "pricingKey": self.pricing_key,
#                 "ratePlanCode": str(unit.get("rate_id", "")),

#                 "discountedPriceWithTaxAndFees": round(final_price, 2),
#                 "totalTaxWithFees": round(tax, 2),
#                 "totalAdditionalFees": 0.0,
#             }
#         }


# # =========================================================
# # Hotel Mapper (LOGIC PRESERVED)
# # =========================================================

# class HotelMapper:

#     def map(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         hotels = self._extract_hotels(data)
#         mapped_hotels = [self._map_hotel(h) for h in hotels]

#         return {
#             "response": {
#                 "personalizedSections": [
#                     {
#                         "hotels": mapped_hotels
#                     }
#                 ]
#             }
#         }

#     def _extract_hotels(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         if "hotel" in data and isinstance(data["hotel"], dict):
#             return [data["hotel"]]

#         sr = data.get("searchResult", {})
#         if isinstance(sr, dict) and isinstance(sr.get("his"), list):
#             return [h for h in sr["his"] if isinstance(h, dict)]

#         if isinstance(data, dict) and data.get("name"):
#             return [data]

#         return []

#     def _map_hotel(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
#         ad = hotel.get("ad", {})

#         city_name = (
#             (ad.get("city") or {}).get("name")
#             or ad.get("ctn")
#             or ""
#         )

#         country_name = (ad.get("country") or {}).get("name") or ""

#         gl = hotel.get("gl", {})

#         lat = _Utils.safe_float(gl.get("lt"))
#         lng = _Utils.safe_float(gl.get("ln"))

#         return {
#             "id": str(hotel.get("id", "")),
#             "name": hotel.get("name", ""),
#             "starRating": int(hotel.get("rt", 0)),

#             "locationDetail": {
#                 "name": city_name,
#                 "countryName": country_name
#             },

#             "geoLocation": {
#                 "latitude": lat,
#                 "longitude": lng
#             },

#             "media": self._to_media(hotel)
#         }

#     def _to_media(self, hotel: Dict[str, Any]) -> List[Dict[str, str]]:
#         media: List[Dict[str, str]] = []

#         imgs = hotel.get("imgs")

#         if isinstance(imgs, list):
#             for item in imgs:
#                 if isinstance(item, str):
#                     media.append({"url": item})
#                 elif isinstance(item, dict):
#                     url = item.get("url") or item.get("u")
#                     if url:
#                         media.append({"url": url})

#         if not media:
#             img = hotel.get("img")
#             if isinstance(img, str):
#                 media.append({"url": img})
#             elif isinstance(img, dict):
#                 url = img.get("url") or img.get("u")
#                 if url:
#                     media.append({"url": url})

#         return media


# # =========================================================
# # Description Mapper (LOGIC PRESERVED)
# # =========================================================

# class DescriptionMapper:

#     def map(self, hotel: Dict[str, Any]) -> Dict[str, Any]:
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

#     def _safe_parse(self, raw: str) -> Dict[str, Any]:
#         try:
#             return json.loads(raw)
#         except Exception:
#             return {}

#     def _format_title(self, key: str) -> str:
#         return key.replace("_", " ").title()


# # =========================================================
# # Aggregator (ENTRY POINT)
# # =========================================================

# class TripjackMapper:

#     def __init__(self):
#         self.hotel_mapper = HotelMapper()
#         self.price_mapper = PriceMapper()
#         self.desc_mapper = DescriptionMapper()

#     def map(self, data: Dict[str, Any]) -> Dict[str, Any]:

#         # Step 1: Hotel structure
#         hotel_response = self.hotel_mapper.map(data)

#         hotels = hotel_response.get("response", {}) \
#                                 .get("personalizedSections", [{}])[0] \
#                                 .get("hotels", [])

#         if not hotels:
#             return hotel_response

#         hotel = hotels[0]

#         raw_hotel = data.get("hotel", data)

#         # Step 2: Price
#         price_data = self.price_mapper.map(data)

#         if not isinstance(price_data, list):
#             price_data = [price_data]

#         rooms = []
#         for price in price_data:
#             rooms.append({
#                 "priceDetail": price.get("priceDetail", {})
#             })

#         # Step 3: Description
#         desc_data = self.desc_mapper.map(raw_hotel)

#         # Step 4: Inject
#         hotel["rooms"] = rooms
#         hotel["descriptionSections"] = desc_data.get("descriptionSections", [])

#         return hotel_response


# # =========================================================
# # Local Test
# # =========================================================

# if __name__ == "__main__":
#     try:
#         with open("tripjack.json", "r") as f:
#             data = json.load(f)

#         mapper = TripjackMapper()
#         result = mapper.map(data)

#         # ---------- SAVE OUTPUT ----------
#         output_file = "mapped_output.json"

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(result, f, indent=2, ensure_ascii=False)

#         print(f"\n✅ Output saved to: {output_file}")

#     except Exception as e:
#         print("Error:", str(e))