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

