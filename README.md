# Hotel Data Chunking using RabbitMQ DAY 1

## Overview
This project demonstrates how to process large hotel search data by splitting it into smaller chunks and sending it through RabbitMQ for efficient handling.

## Features
- Parse nested hotel search JSON
- Chunk large datasets
- Asynchronous message handling using RabbitMQ
- Producer-consumer architecture

## Workflow
1. Input JSON contains hotel search data
2. Data is chunked into smaller groups
3. Each chunk is sent to RabbitMQ
4. Consumer receives and processes chunks

## Tech Used
- Python
- RabbitMQ
- Pika library

## Learning Outcome
- Understanding of message queues
- Handling large datasets efficiently
- Backend system design for scalable applications

# Hotel Data Chunking using RabbitMQ DAY 2

## Overview
This project demonstrates how to process large hotel search data by splitting it into smaller chunks and sending it through RabbitMQ for efficient handling.

## Features
- Parse nested hotel search JSON
- Chunk large datasets into smaller pieces
- Asynchronous communication using RabbitMQ
- Producer-consumer architecture
- Controlled message processing using ACK mechanism

## Workflow
1. Input JSON contains hotel search data
2. Backend extracts hotel list from nested structure
3. Data is divided into chunks
4. Each chunk is pushed to RabbitMQ queue
5. Consumer processes chunks sequentially using ACK

## Tech Stack
- Python
- RabbitMQ
- Pika

## Key Concepts Learned
- Message Queue (RabbitMQ)
- Asynchronous processing
- Chunk-based data handling
- Producer-Consumer architecture
- Debugging data flow in backend systems

## Future Improvements
- Integrate with Django API
- Optimize message payload
- Implement frontend infinite scroll support

# Day 3 - Response Mapping Layer (Tripjack → MakeMyTrip)

## 📌 Overview

Today’s task was to implement a **response mapping layer** to standardize API output across providers.

The goal was to transform the deeply nested **Tripjack API response** into a structure compatible with **MakeMyTrip (MMT) room selection response**, based on actual data observed via Chrome DevTools.

This is not simple JSON transformation — it is a **semantic transformation problem**, especially for pricing.

---

## 🎯 Objective

- Extract relevant data from deeply nested Tripjack response
- Map pricing (`fc` block) into MMT `priceDetail` schema
- Ensure output matches **MMT UI behavior**, not just JSON structure
- Build reusable Python class for mapping
- Validate logic using real data

---

## 🧠 Core Challenge

Tripjack and MMT use **different pricing philosophies**:

### Tripjack (Backend / Financial Model)
- Provides raw pricing components:
  - BF (Base Fare)
  - SGP / TF (Total Fare)
  - TTSF (Tax)
  - TMF (Markup)
  - SAC (Additional fees)

### MakeMyTrip (Frontend / UX Model)
- Provides user-friendly pricing:
  - displayPrice → shown price (excluding tax)
  - price → original (strike-through)
  - discountedPrice → same as displayPrice
  - discountedPriceWithTax → final payable

👉 **Conclusion:**  
Mapping is NOT 1:1 — it requires **deriving values intelligently**

---

## 🏗️ Implementation

### Step 1: Data Extraction

Traversed nested structure:

searchResult → his → ops → ris → pis → fc

Extracted all `fc` nodes safely using `.get()` and loops (no hardcoded indexing).

---

### Step 2: Initial Mapping Attempt (WRONG)

Initial assumption:

displayPrice = BF + TMF  
finalPrice = displayPrice + tax  

❌ Problem:
- Did not match actual MMT UI
- Ignored how MMT derives display vs discounted pricing

---

### Step 3: UI-Based Understanding

From real UI:

₹5,874 (strike-through)  
₹4,699 + ₹235 tax  

Derived:

displayPrice = discounted base price  
finalPrice = displayPrice + tax  

---

### Step 4: Second Mapping Attempt (PARTIALLY WRONG)

Used:

displayPrice = final_price - tax  

✔ Mathematically correct  
❌ Semantically risky  

---

## 🚨 Critical Bug Discovered

Tripjack data inconsistency:

"BF": 538.82  
"SGP": 538.82  
"TTSF": 26.33  

👉 This breaks assumption:

SGP ≠ base + tax  

---

## 🔥 Root Problem

Tripjack fields are **not reliable individually**.

- BF sometimes includes tax  
- SGP sometimes equals BF  
- Derived calculations become unsafe  

---

## ✅ Final Correct Strategy

Always prefer **explicit fields over derived ones**

### Final Logic:

final_price = SGP or TF  
tax = TTSF or TSF  

discounted_base = SBP or SNP or (final_price - tax)  
original_price = discounted_base + TMF  

---

## 💡 Final Mapping Logic

displayPrice = discounted_base  
discountedPrice = discounted_base  
price = original_price  
discountedPriceWithTax = final_price  
priceWithTax = original_price + tax  
totalTax = tax  
totalTaxWithFees = tax  
totalAdditionalFees = SAC  

---

## ⚠️ Mistakes That Wasted Time

### ❌ Mistake 1: Trusting formulas blindly
Assumed:
final - tax = base  
→ Not true in real APIs  

---

### ❌ Mistake 2: Treating APIs as clean systems
Reality:
- Aggregator APIs are inconsistent  
- Fields may overlap or contradict  

---

### ❌ Mistake 3: Using BF as base price
→ Sometimes BF already includes tax  

---

### ❌ Mistake 4: Ignoring UI behavior
Focused only on JSON, not on:
- What user sees  
- How price is displayed  

---

## 🧪 Verification

- Ran mapper on real Tripjack JSON  
- Output:
  - 13 priceDetail objects  

### Verified:
- displayPrice + tax = final price ✔  
- Output structure matches MMT ✔  
- No crashes on missing fields ✔  

---

## ✅ What Was Achieved

- Built reusable mapping class  
- Implemented safe nested traversal  
- Correctly aligned pricing with MMT UI  
- Identified unreliable API fields  
- Learned how to handle real-world data inconsistencies  

---

## ❗ What Is Still Missing

- Full hotel + room mapping (only priceDetail done)  
- ratePlanCode mapping (currently empty)  
- Support for multiple providers (RateHawk etc.)  
- Proper pricing strategy abstraction  
- Unit testing for mapping logic  

---

## ⚠️ What Is Still Confusing / Risky

- TMF meaning (markup vs discount)  
- Difference between SBP, SNP, BF  
- When SGP includes tax vs not  
- SAC handling (should it be visible or hidden?)  

---

## 🧠 Key Learnings

- API mapping ≠ field renaming → it is **semantic transformation**  
- Always validate against UI, not just API docs  
- Never trust a single field in aggregator APIs  
- Prefer:
  explicit fields > derived calculations  
- Backend pricing ≠ frontend pricing  

---

## 🔮 Next Steps

- Implement full response mapper:
  - hotel-level  
  - room-level  
  - rate-level  
- Introduce pricing strategy layer  
- Handle edge cases (missing / inconsistent data)  
- Prepare for multi-provider standardization  

---

## 🧩 Final Insight

This task is part of building a:

Standardization Layer (Aggregator Backend)

Where:

Tripjack / RateHawk / Others  
        ↓  
Normalization Layer  
        ↓  
Common Output Schema (MMT-like)  

---

## 🚀 Summary

This was not just a coding task.

This was:
- Understanding broken real-world data  
- Designing a transformation layer  
- Aligning backend logic with frontend UX  

This is actual backend engineering, not tutorial code.