import { config } from "../config";
import { ApiError } from "../types";

/**
 * Represents an authenticated request context.
 * Task 2 will add rate-limiting middleware alongside this.
 */
export interface AuthContext {
  userId: string;
  role: "admin" | "member" | "guest";
}

/**
 * Simple auth middleware that validates Bearer tokens.
 * Returns the authenticated context or throws an ApiError.
 *
 * In this scaffold, tokens are simple base64-encoded JSON:
 *   Buffer.from(JSON.stringify({ userId, role })).toString("base64")
 */
export function authMiddleware(authHeader: string | undefined): AuthContext {
  if (!authHeader) {
    throw createAuthError("Missing authorization header");
  }

  if (!authHeader.startsWith(config.auth.tokenPrefix)) {
    throw createAuthError("Invalid authorization format — expected Bearer token");
  }

  const token = authHeader.slice(config.auth.tokenPrefix.length);

  try {
    const decoded = JSON.parse(
      Buffer.from(token, "base64").toString("utf-8")
    );

    if (!decoded.userId || !decoded.role) {
      throw createAuthError("Malformed token payload");
    }

    return {
      userId: decoded.userId,
      role: decoded.role,
    };
  } catch (err) {
    if ((err as ApiError).code === "AUTH_ERROR") {
      throw err;
    }
    throw createAuthError("Invalid token encoding");
  }
}

/**
 * Helper to create a standardized auth error.
 */
export function createAuthError(message: string): ApiError {
  return {
    code: "AUTH_ERROR",
    message,
  };
}

/**
 * Creates a valid test token for use in tests.
 */
export function createTestToken(userId: string, role: string): string {
  return Buffer.from(JSON.stringify({ userId, role })).toString("base64");
}
