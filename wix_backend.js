import { ok, badRequest, forbidden, serverError } from 'wix-http-functions';
import { ok } from 'wix-http-functions';

export function debug_test(request) {
  return ok({
    headers: { "Content-Type": "application/json" },
    body: {
      status: "reachable",
      message: "You’ve reached Wix backend!"
    }
  });
}
// Shared secret — must match the one used in Flask
const SHARED_SECRET = "michael-2025-secret-key";  // 🔐 Replace if needed

export function post_receive(request) {
  // Step 1: Check shared secret in headers
  const receivedKey = request.headers["x-api-key"];
  if (receivedKey !== SHARED_SECRET) {
    console.warn("🚫 Invalid API key received:", receivedKey);
    return forbidden({
      body: { error: "Invalid API key" }
    });
  }

  // Step 2: Parse JSON body
  return request.body.json()
    .then((body) => {
      console.log("✅ JSON received from Flask:", body);

      return ok({
        headers: { "Content-Type": "application/json" },
        body: {
          status: "received",
          receivedAt: new Date().toISOString(),
          echo: body
        }
      });
    })
    .catch((err) => {
      console.error("❌ JSON parse error:", err.message);
      return badRequest({
        body: { error: "Invalid JSON format", detail: err.message }
      });
    });
}