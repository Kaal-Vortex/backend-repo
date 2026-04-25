# #Chatgpt interview prep for django - DAY 4

from typing import Any, Dict, List
import json


class TripjackToMMTMapper:
    """
    Final production mapper:
    Tripjack → MakeMyTrip priceDetail (UI-aligned)
    """

    def __init__(self, pricing_key: str = "DEFAULT"):
        self.pricing_key = pricing_key

    # ---------- Public API ----------
    def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Entry point
        """
        hotel = data.get("hotel", data)  # support both wrapped and direct

        price_units = self._extract_rooms(hotel)
        return [self._map_price_detail(unit) for unit in price_units]

    # ---------- Extraction ----------
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

    # ---------- Safe Float ----------
    def _safe_float(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    # ---------- Mapping ----------
    def _map_price_detail(self, unit: Dict[str, Any]) -> Dict[str, Any]:
        tp = self._safe_float(unit.get("tp"))

        tfcs = unit.get("tfcs", {})
        tafcs = unit.get("tafcs", {}).get("TAF", {})

        # Core values (LOCKED LOGIC)
        display_price = self._safe_float(tfcs.get("BF"))
        tax = self._safe_float(tfcs.get("TAF"))
        final_price = tp or self._safe_float(tfcs.get("TF"))

        strike_price = self._safe_float(tafcs.get("SBP"))

        # Fallbacks (minimal, safe)
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
                "totalAdditionalFees": 0.0,  # intentionally hidden
            }
        }


# ---------- Local Test ----------
if __name__ == "__main__":
    try:
        with open("tripjack.json", "r") as f:
            data = json.load(f)

        mapper = TripjackToMMTMapper()
        result = mapper.map(data)

        print("\n--- Mapped Output (first 3) ---\n")
        for item in result[:3]:
            print(json.dumps(item, indent=2))

        print(f"\nTotal mapped priceDetails: {len(result)}")

    except FileNotFoundError:
        print("Error: tripjackResponse.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")

#---------------------------TOTALY WRONG SCHEMA USED FOR TRIPJACK------------------------------------

# #Chatgpt interview prep for django - improved

# from typing import Any, Dict, List
# import json


# class TripjackToMMTMapper:
#     """
#     Reusable mapper for converting Tripjack response to
#     MakeMyTrip priceDetail schema (MMT-aligned pricing logic).
#     """

#     def __init__(self, pricing_key: str = "DEFAULT"):
#         self.pricing_key = pricing_key

#     # ---------- Public API ----------
#     def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """
#         End-to-end mapping:
#         extract all fc nodes → map each to MMT priceDetail
#         """
#         fcs = self._extract_fcs(data)
#         return [self._map_price_detail(fc) for fc in fcs]

#     # ---------- Internal Helpers ----------
#     def _extract_fcs(self, data: Dict[str, Any]) -> List[Dict[str, float]]:
#         """
#         Traverse:
#         searchResult → his → ops → ris → pis → fc
#         """
#         fcs: List[Dict[str, float]] = []

#         for hotel in data.get("searchResult", {}).get("his", []):
#             for op in hotel.get("ops", []):
#                 for room in op.get("ris", []):
#                     for price_item in room.get("pis", []):
#                         fc = price_item.get("fc")
#                         if isinstance(fc, dict):
#                             fcs.append(fc)

#         return fcs

#     def _map_price_detail(self, fc: Dict[str, float]) -> Dict[str, Any]:
#         """
#         MMT-aligned pricing logic based on real UI behavior:
#         - displayPrice = discounted base (final - tax)
#         - price = original (display + markup)
#         - discountedPriceWithTax = final payable
#         """

#         # --- Extract values safely ---
#         final_price = float(fc.get("SGP") or fc.get("TF", 0.0))
#         tax = float(fc.get("TTSF") or fc.get("TSF", 0.0))
#         markup = float(fc.get("TMF", 0.0))
#         additional_fee = float(fc.get("SAC", 0.0))

#         # --- Derived values (MMT logic) ---
#         discounted_base = final_price - tax  # shown price
#         original_price = discounted_base + markup  # strike-through price

#         return {
#             "priceDetail": {
#                 # Base display
#                 "displayPrice": round(discounted_base, 2),
#                 "price": round(original_price, 2),

#                 # With tax
#                 "priceWithTax": round(original_price + tax, 2),

#                 # Discounted values
#                 "discountedPrice": round(discounted_base, 2),
#                 "discountedPriceWithTax": round(final_price, 2),

#                 # Tax details
#                 "totalTax": round(tax, 2),

#                 # Static / configurable
#                 "pricingKey": self.pricing_key,
#                 "ratePlanCode": "",  # populate if available

#                 # Extended fields
#                 "discountedPriceWithTaxAndFees": round(final_price, 2),
#                 "totalTaxWithFees": round(tax + additional_fee, 2),
#                 "totalAdditionalFees": round(additional_fee, 2),
#             }
#         }


# # ---------- Test / Local Execution ----------
# if __name__ == "__main__":
#     """
#     Runs only when executed directly (not when imported).
#     """

#     try:
#         with open("tripjackResponse.json", "r") as f:
#             data = json.load(f)

#         mapper = TripjackToMMTMapper()
#         result = mapper.map(data)

#         print("\n--- Mapped Output (first 3) ---\n")
#         for item in result[:3]:
#             print(json.dumps(item, indent=2))

#         print(f"\nTotal mapped priceDetails: {len(result)}")

#     except FileNotFoundError:
#         print("Error: 'tripjackResponse.json' not found.")
#     except json.JSONDecodeError:
#         print("Error: Invalid JSON format.")

# #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# #OR

# #chatgpt interview prep for django

# # from typing import Any, Dict, List
# # import json


# # class TripjackToMMTMapper:
# #     """
# #     Reusable mapper for converting Tripjack response to
# #     MakeMyTrip priceDetail schema.
# #     """

# #     def __init__(self, pricing_key: str = "DEFAULT"):
# #         self.pricing_key = pricing_key

# #     # ---------- Public API ----------
# #     def map(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         """
# #         End-to-end mapping:
# #         extract all fc nodes → map each to MMT priceDetail
# #         """
# #         fcs = self._extract_fcs(data)
# #         return [self._map_price_detail(fc) for fc in fcs]

# #     # ---------- Internal Helpers ----------
# #     def _extract_fcs(self, data: Dict[str, Any]) -> List[Dict[str, float]]:
# #         """
# #         Traverse:
# #         searchResult → his → ops → ris → pis → fc
# #         """
# #         fcs: List[Dict[str, float]] = []

# #         for hotel in data.get("searchResult", {}).get("his", []):
# #             for op in hotel.get("ops", []):
# #                 for room in op.get("ris", []):
# #                     for price_item in room.get("pis", []):
# #                         fc = price_item.get("fc")
# #                         if isinstance(fc, dict):
# #                             fcs.append(fc)

# #         return fcs

# #     def _map_price_detail(self, fc: Dict[str, float]) -> Dict[str, Any]:
# #         """
# #         Map Tripjack fare component (fc) to MMT priceDetail.
# #         """

# #         base_price = float(fc.get("BF", 0.0))
# #         total_price = float(fc.get("SGP") or fc.get("TF", 0.0))
# #         total_tax = float(fc.get("TTSF") or fc.get("TSF", 0.0))
# #         markup = float(fc.get("TMF", 0.0))
# #         additional_fees = float(fc.get("SAC", 0.0))

# #         # Conservative derivation
# #         discounted_price = total_price - markup if markup else total_price

# #         return {
# #             "priceDetail": {
# #                 "displayPrice": round(total_price, 2),
# #                 "price": round(base_price, 2),
# #                 "priceWithTax": round(total_price, 2),

# #                 "discountedPrice": round(discounted_price, 2),
# #                 "discountedPriceWithTax": round(discounted_price, 2),

# #                 "totalTax": round(total_tax, 2),

# #                 "pricingKey": self.pricing_key,
# #                 "ratePlanCode": "",  # populate if available upstream

# #                 "discountedPriceWithTaxAndFees": round(discounted_price, 2),
# #                 "totalTaxWithFees": round(total_tax, 2),
# #                 "totalAdditionalFees": round(additional_fees, 2),
# #             }
# #         }


# # # ---------- Test / Local Execution ----------
# # if __name__ == "__main__":
# #     """
# #     This block runs ONLY when executing this file directly.
# #     It will NOT run when the class is imported elsewhere.
# #     """

# #     # Replace with your actual file path
# #     with open("tripjackResponse.json", "r") as f:
# #         data = json.load(f)

# #     mapper = TripjackToMMTMapper()
# #     result = mapper.map(data)

# #     print("\nMapped Output (first 3):\n")
# #     for item in result[:3]:
# #         print(json.dumps(item, indent=2))

# #     print(f"\nTotal mapped priceDetails: {len(result)}")

# # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# # OR

# #Gemini improved

# # import json

# # class TripjackToMMTMapper:
# #     """
# #     Standardizes Deeply Nested Tripjack API responses into 
# #     MakeMyTrip (MMT) Frontend schemas.
# #     """

# #     def map(self, tj_raw: dict) -> list:
# #         """
# #         Drills down through the Tripjack hierarchy to extract and transform
# #         every price detail into an MMT-compatible list.
# #         """
# #         all_mapped_prices = []

# #         # Drill down: searchResult -> his[] -> ops[] -> ris[] -> pis[]
# #         search_results = tj_raw.get("searchResult", {})
        
# #         for hotel in search_results.get("his", []):
# #             for option in hotel.get("ops", []):
# #                 for room in option.get("ris", []):
# #                     for price_info in room.get("pis", []):
                        
# #                         # Extract the Fare Components (fc)
# #                         fc = price_info.get("fc", {})
                        
# #                         # Generate the MMT priceDetail structure
# #                         mapped_detail = self._transform_price(fc, price_info.get("id"))
# #                         all_mapped_prices.append(mapped_detail)
        
# #         return all_mapped_prices

# #     def _transform_price(self, fc: dict, rate_id: str) -> dict:
# #         """Internal helper to map specific keys and hide internal margins."""
# #         total_payable = fc.get("TF", 0.0)
# #         base_fare = fc.get("BF", 0.0)
# #         markup = fc.get("TMF", 0.0)
# #         taxes = fc.get("TTSF", 0.0)
# #         service_acc = fc.get("SAC", 0.0)

# #         return {
# #             "priceDetail": {
# #                 "displayPrice": int(fc.get("SGP", 0.0)),
# #                 "price": int(base_fare + markup),
# #                 "priceWithTax": int(total_payable + service_acc),
# #                 "discountedPrice": int(fc.get("SGP", 0.0)),
# #                 "discountedPriceWithTax": int(total_payable),
# #                 "totalTax": int(taxes),
# #                 "pricingKey": "DEFAULT",
# #                 "ratePlanCode": str(rate_id),
# #                 "discountedPriceWithTaxAndFees": int(total_payable),
# #                 "totalTaxWithFees": int(taxes + service_acc),
# #                 "totalAdditionalFees": 0
# #             }
# #         }

# # if __name__ == "__main__":
# #     """
# #     This block runs ONLY when executing this file directly.
# #     It will NOT run when the class is imported elsewhere.
# #     """

# #     try:
# #         # 1. Load the actual API response from your local file
# #         with open("tripjackResponse.json", "r") as f:
# #             data = json.load(f)

# #         # 2. Initialize and Map
# #         mapper = TripjackToMMTMapper()
# #         result = mapper.map(data)

# #         # 3. Validation Output
# #         print("\n--- Mapped Output (first 3) ---")
# #         for item in result[:3]:
# #             print(json.dumps(item, indent=2))

# #         print(f"\nTotal mapped priceDetails: {len(result)}")

# #     except FileNotFoundError:
# #         print("Error: 'tripjackResponse.json' not found. Please ensure the file exists in the same directory.")
# #     except json.JSONDecodeError:
# #         print("Error: Failed to decode JSON. Check the format of your input file.")

# # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# # OR

# #Gemini

# # import json

# # class TravelAPIMapper:
# #     """
# #     Standardizes Deeply Nested Tripjack API responses into 
# #     MakeMyTrip (MMT) Frontend schemas.
# #     """

# #     def transform_tripjack_to_mmt(self, tj_raw: dict) -> dict:
# #         # Initialize the MMT skeleton
# #         mmt_response = {
# #             "response": {
# #                 "personalizedSection": {
# #                     "hotels": []
# #                 }
# #             }
# #         }

# #         # 1. Access the search results
# #         search_results = tj_raw.get("searchResult", {})
        
# #         # 2. Loop through Hotels (his)
# #         for hotel in search_results.get("his", []):
# #             mmt_hotel_entry = {
# #                 "hotelId": hotel.get("id"), # Example of mapping hotel ID
# #                 "priceDetail": {}
# #             }

# #             # 3. Loop through Options (ops) -> Rooms (ris) -> Price Info (pis)
# #             # Usually, we take the first price available for the main listing
# #             for option in hotel.get("ops", []):
# #                 for room in option.get("ris", []):
# #                     for price_info in room.get("pis", []):
                        
# #                         # Extract the Fare Components (fc)
# #                         fc = price_info.get("fc", {})
                        
# #                         # Perform the specific mapping logic
# #                         mmt_hotel_entry["priceDetail"] = self._map_price(fc, price_info.get("id"))
                        
# #                         # Once we find the primary price, we break (or continue based on logic)
# #                         break 
            
# #             # Append the mapped hotel to our list
# #             mmt_response["response"]["personalizedSection"]["hotels"].append(mmt_hotel_entry)

# #         return mmt_response

# #     def _map_price(self, fc: dict, rate_id: str) -> dict:
# #         """Helper to create the MMT price object without leaking Net Fares."""
# #         total_payable = fc.get("TF", 0.0)
# #         base_fare = fc.get("BF", 0.0)
# #         markup = fc.get("TMF", 0.0)
# #         taxes = fc.get("TTSF", 0.0)
# #         service_acc = fc.get("SAC", 0.0)

# #         return {
# #             "displayPrice": int(fc.get("SGP", 0.0)),
# #             "price": int(base_fare + markup),
# #             "priceWithTax": int(total_payable + service_acc),
# #             "discountedPrice": int(fc.get("SGP", 0.0)),
# #             "discountedPriceWithTax": int(total_payable),
# #             "totalTax": int(taxes),
# #             "pricingKey": "DEFAULT",
# #             "ratePlanCode": str(rate_id),
# #             "discountedPriceWithTaxAndFees": int(total_payable),
# #             "totalTaxWithFees": int(taxes + service_acc),
# #             "totalAdditionalFees": 0
# #         }

# # # --- Direct Execution for Testing ---
# # if __name__ == "__main__":
# #     # Mocking your deeply nested Tripjack response
# #     mock_tripjack = {
# #         "searchResult": {
# #             "his": [
# #                 {
# #                     "id": "HTL-123",
# #                     "ops": [{
# #                         "ris": [{
# #                             "pis": [{
# #                                 "fc": {
# #                                     "CMU": 0.0, "SNP": 495.7, "SGP": 538.82,
# #                                     "TMF": 43.12, "BF": 538.82, "TTSF": 26.33,
# #                                     "TF": 538.82, "NF": 400.0 # Hidden!
# #                                 }
# #                             }]
# #                         }]
# #                     }]
# #                 }
# #             ]
# #         }
# #     }

# #     mapper = TravelAPIMapper()
# #     final_output = mapper.transform_tripjack_to_mmt(mock_tripjack)

# #     print("--- TRANSFORMATION SUCCESSFUL ---")
# #     print(json.dumps(final_output, indent=4))

