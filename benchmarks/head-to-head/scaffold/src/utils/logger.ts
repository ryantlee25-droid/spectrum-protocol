import { config, LogLevel } from "../config";

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

/**
 * Simple structured logger.
 * Respects the configured log level from config.ts.
 */
export function log(level: LogLevel, message: string, meta?: Record<string, unknown>): void {
  if (LOG_LEVELS[level] < LOG_LEVELS[config.logging.level]) {
    return;
  }

  const entry: Record<string, unknown> = {
    level,
    message,
  };

  if (config.logging.timestamp) {
    entry.timestamp = new Date().toISOString();
  }

  if (meta) {
    entry.meta = meta;
  }

  // In a real app this would go to a transport; here we just console.log
  // Tests can spy on console.log to verify logging behavior
  console.log(JSON.stringify(entry));
}

/**
 * Creates a child logger with pre-filled metadata.
 */
export function createLogger(context: Record<string, unknown>) {
  return {
    debug: (msg: string, meta?: Record<string, unknown>) =>
      log("debug", msg, { ...context, ...meta }),
    info: (msg: string, meta?: Record<string, unknown>) =>
      log("info", msg, { ...context, ...meta }),
    warn: (msg: string, meta?: Record<string, unknown>) =>
      log("warn", msg, { ...context, ...meta }),
    error: (msg: string, meta?: Record<string, unknown>) =>
      log("error", msg, { ...context, ...meta }),
  };
}
