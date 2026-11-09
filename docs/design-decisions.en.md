# Architecture & Design Decisions

This document outlines the key architectural choices, trade-offs, and constraints made during the development of the Mini AdTech Platform MVP.

## One Site per Publisher & Simplified Ad Model

To minimize complexity for the MVP, the system assumes a single dedicated domain per publisher without the concept of multiple AdSlots. While this limits layout flexibility, it accelerates initial deployment.

## Reporting & Aggregation Strategy

Real-time reporting is performed directly from raw transaction tables, which poses scalability risks. To mitigate this, a future transition to asynchronous aggregation using Celery is planned.

Timezone Alignment: Reporting aggregation follows the UTC day cycle (starting at 03:30 AM Tehran time).

## Concurrency Control in Budget Management

Mechanism: To mitigate the risk of budget overruns during concurrent requests, select_for_update and atomic transactions are used to manage budget deductions.

Verification Status: While the logic is covered by Unit Tests to ensure functional correctness, it has not yet been subjected to high-concurrency stress testing (multithreading/load testing) to verify behavior under extreme real-world conditions.

## Impression-to-Click Relationship

Integrity Mechanism: A strict 1:1 relationship between an impression and a click is enforced via a Database-level Unique Constraint. This serves as the primary defense against duplicate click injection and race conditions.

Optimization: The exists() check in the application logic is used strictly as an optimization to prevent unnecessary budget calculations and heavy database operations for duplicate click attempts.

## Signed Click Tokens

Integrity: Click requests are validated using Django’s TimestampSigner to ensure the click data hasn’t been tampered with (Integrity).

Time-Window: A 1-hour expiration is applied to limit the window of opportunity for potential misuse.

Replay Prevention: Note that the signature alone does not prevent replay attacks; protection against replay is strictly enforced by the 1:1 relationship between an Impression and a Click (see Impression-to-Click Relationship).

## IP Identification & Proxy Trust

Current Implementation: Client IP detection currently relies on the X-Forwarded-For header, which is suitable for development environments behind a known proxy.

Security Warning: This implementation is vulnerable to IP spoofing because the header can be manipulated by the client. In a production environment, IP identification must only be trusted if the request originates from a verified and trusted proxy (e.g., Nginx or a Cloud Load Balancer) to prevent attackers from bypassing IP-based restrictions.

## Simplified Ad Selection Logic

Ad selection is implemented using values_list and random.choice for performance, intentionally omitting complex targeting or ranking algorithms in this MVP phase.

## Security via Error Masking (404 for Blocked Publishers)

Public Endpoints: To prevent information leakage regarding the system’s internal state or the existence of specific publishers, blocked publishers return a 404 Not Found instead of a 403 Forbidden. The response body for these 404 errors is kept generic to avoid revealing any details.

Authenticated Dashboard: For authenticated publishers, the system is designed to return a transparent 403 Forbidden status with a clear reason for the block (e.g., “Account Suspended”), ensuring a better user experience for legitimate users.

## Blocked Publisher Click Policy (Current Limitation & Future Roadmap)

Current State: Currently, clicks on blocked publishers are still recorded and processed, leading to unauthorized budget consumption. The security window is temporarily limited to the 1-hour token expiration.

Required Implementation: To fix this, a is_valid_click flag must be added to the Click model. This requires updating five core functions: Budget Management (two functions), CTR Calculation, get_campaign_report, and Top Campaigns.

Goal: Future updates will implement a “Log-Flag-Settle” mechanism to ensure clicks from invalid publishers are recorded for audit but excluded from financial settlements.

## Sensitive Data Handling (Plaintext Limitation)

Bank card numbers are currently stored as plaintext for MVP simplicity, acknowledging that production environments require robust encryption (e.g., AES).

## Environment & Infrastructure Constraints

Database Selection: The architecture utilizes Neon for managed PostgreSQL. This choice was driven by version compatibility requirements: Django 4.2 requires PostgreSQL version 12 or higher, while the available local/alternative environments were limited to version 10 (32-bit), which is incompatible with the current project requirements.

Deferred Components: Integration with Redis and Docker is currently deferred to focus on core logic and simplify the initial development workflow.

## Budget as a Derived State (Real-time Accuracy)

**Mechanism:** Instead of maintaining a mutable "Remaining Budget" field in the
Campaign model, budget consumption is calculated dynamically by aggregating the
`Click` records.

**Trade-off (Accuracy vs. Performance):**
- **Pros:** Ensures absolute data integrity and eliminates the need for nightly
  reset jobs or complex Celery tasks to sync totals. It prevents "drift" between
  recorded clicks and reported spending.
- **Cons:** Increases computational cost per click due to aggregation queries.
  This is identified as a performance bottleneck to be addressed in a later
  phase through a caching layer (e.g., Redis, if the environment allows) or a
  daily aggregation table.

Note on Daily Cycle: The budget reset cycle is synchronized with the UTC midnight, which corresponds to 03:30 AM Tehran time.

## CTR Calculation: Zero vs. None (Ordering Logic)

**Problem:** A discrepancy exists between returning `None` (when a single campaign has no data) and using `0` (during ranking/sorting operations).

**Technical Rationale:** 

- **PostgreSQL NULL Handling:** In PostgreSQL, `NULL` values are treated as *larger* than any non-null value. Consequently, in an `ORDER BY ... DESC` clause, `NULL` values appear *first*. This would incorrectly push campaigns with zero activity (or no clicks) to the top of performance rankings.

- **Design Decision:** We explicitly use `0` during ranking queries so that zero-activity campaigns are correctly positioned at the bottom of the list. Meanwhile, single-campaign views return `None` to semantically distinguish between "no data available" and an actual "0% CTR".

- **Safety:** The implementation in `get_top_campaigns` uses `Case/When` expressions to prevent division-by-zero errors when impressions are zero.

