# Architecture & Design Decisions
 This document outlines the key architectural choices, trade-offs, and constraints made during the development of the Mini AdTech Platform MVP.

## One Site per Publisher & Simplified Ad Model
 To minimize complexity for the MVP, the system assumes a single dedicated domain per publisher without the concept of multiple AdSlots. While this limits layout flexibility, it accelerates initial deployment.

## Reporting & Aggregation Strategy
 Real-time reporting is performed directly from raw transaction tables, which poses scalability risks. To mitigate this, a future transition to asynchronous aggregation using Celery is planned.

## Concurrency Control in Budget Management
 To prevent budget overruns during high-concurrency requests, select_for_update and atomic transactions are implemented to ensure strict data consistency.

## Impression-to-Click Relationship
 A strict 1:1 relationship between an impression and a click is enforced via a OneToOneField and exists() checks to prevent click fraud; this serves as the primary defense against duplicate click injection.

## Signed Click Tokens
 Click requests are validated using Django’s TimestampSigner with a 1-hour expiration to prevent replay attacks and ensure the integrity of the click event.

## IP Identification & Proxy Trust
 Client IP detection relies on the X-Forwarded-For header, assuming a trusted proxy environment to accurately identify end-users.

## Simplified Ad Selection Logic
 Ad selection is implemented using values_list and random.choice for performance, intentionally omitting complex targeting or ranking algorithms in this MVP phase.

## Security via Error Masking (404 for Blocked Publishers)
 To prevent information leakage about the system’s internal state, blocked publishers return a 404 Not Found instead of a 403 Forbidden on public endpoints.

## Blocked Publisher Click Policy
 Clicks from blocked publishers are logged and flagged for auditing but excluded from financial settlements to balance data integrity with revenue protection.

## Sensitive Data Handling (Plaintext Limitation)
 Bank card numbers are currently stored as plaintext for MVP simplicity, acknowledging that production environments require robust encryption (e.g., AES).

## Environment & Infrastructure Constraints
 The architecture utilizes Neon for managed PostgreSQL, while Redis and Docker integration are currently deferred due to environment-specific constraints.
