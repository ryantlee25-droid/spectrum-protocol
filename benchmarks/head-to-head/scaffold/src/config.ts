/**
 * Application configuration.
 * Centralizes constants used across API endpoints.
 */

export const config = {
  api: {
    defaultPage: 1,
    defaultLimit: 20,
    maxLimit: 100,
  },
  auth: {
    tokenPrefix: "Bearer ",
    headerName: "authorization",
  },
  logging: {
    level: "info" as const,
    timestamp: true,
  },
} as const;

export type LogLevel = "debug" | "info" | "warn" | "error";
