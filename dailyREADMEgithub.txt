# Project Title
Hotel Data Chunking System using RabbitMQ

---

## 📌 Overview
This project demonstrates how to process large hotel search datasets by splitting them into smaller chunks and delivering them asynchronously using RabbitMQ.

---

## 🚀 Features
- Parse nested JSON hotel data
- Chunk large datasets into smaller units
- Asynchronous processing using RabbitMQ
- Producer-Consumer architecture
- Controlled message delivery using ACK mechanism

---

## 🏗️ Architecture


---

## ⚙️ Workflow
1. Input JSON contains hotel search data
2. Extract hotel list from nested structure
3. Split data into chunks
4. Send each chunk to RabbitMQ
5. Consumer processes chunks sequentially

---

## 🛠️ Tech Stack
- Python
- RabbitMQ
- Pika

---

## 📂 Project Structure


---

## 🧠 Key Learnings
- Message Queue systems (RabbitMQ)
- Asynchronous backend processing
- Chunk-based data handling
- Debugging real-world data flow
- Handling large datasets efficiently

---

## 🧪 Testing & Verification
- Verified chunk creation using logs
- Confirmed message flow using consumer
- Validated data consistency (total count vs processed count)

---

## 🔒 Security Note
Sensitive data (API keys, credentials) are excluded using `.gitignore`.

---

## 📈 Future Improvements
- Integrate with Django API
- Optimize payload size
- Implement frontend infinite scrolling
- Add caching (Redis)

---

## 👨‍💻 Author
Your Name

