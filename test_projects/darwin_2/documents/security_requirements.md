# Security Requirements

Given the nature of the application (no user accounts, no persistent sensitive data), the security focus is primarily on service availability and robustness.

## 1. Data Security
- **No PII**: The application does not handle or store any Personally Identifiable Information (PII).
- **Statelessness**: The API is largely stateless, with only the most recent generation being cached temporarily. No long-term data storage is required.

## 2. API Endpoint Protection
- **Input Validation**: All incoming data, especially the `settings` object in the `POST /evolution/run` request, must be rigorously validated to prevent malformed data from crashing the simulation engine. This is the primary defense vector.
- **Rate Limiting**: The `POST /evolution/run` endpoint should be rate-limited (e.g., per IP address) to prevent a single user from overwhelming the server with computationally expensive simulation requests. A suggested limit is 10 runs per minute per IP.

## 3. Denial of Service (DoS) Mitigation
- **Request Size Limits**: The web server should be configured to limit the maximum size of incoming request bodies to prevent large, malicious payloads.
- **Resource Management**: The simulation process should be monitored for excessive memory or CPU usage. If a run exceeds predefined limits, it should be terminated gracefully to protect the server''s stability for other users.

## 4. General Best Practices
- **Dependencies**: Keep all backend dependencies (Python libraries, web server) up-to-date with the latest security patches.
- **Error Handling**: Ensure that internal server errors (HTTP 500) do not leak sensitive information, such as stack traces or file paths, to the client.
