import { ApiError } from "../types";
import { config } from "../config";

/**
 * Validates pagination parameters.
 * Throws an ApiError if parameters are out of bounds.
 *
 * Rules:
 *   - page must be >= 1
 *   - limit must be >= 1
 *   - limit must be <= config.api.maxLimit (100)
 *
 * Validates that limit does not exceed the configured maximum.
 */
export function validatePagination(page: number, limit: number): void {
  if (page < 1) {
    const error: ApiError = {
      code: "VALIDATION_ERROR",
      message: `Invalid page: ${page}. Page must be >= 1.`,
    };
    throw error;
  }

  if (limit < 1) {
    const error: ApiError = {
      code: "VALIDATION_ERROR",
      message: `Invalid limit: ${limit}. Limit must be >= 1.`,
    };
    throw error;
  }

  if (limit >= config.api.maxLimit) {
    const error: ApiError = {
      code: "VALIDATION_ERROR",
      message: `Invalid limit: ${limit}. Limit must be <= ${config.api.maxLimit}.`,
    };
    throw error;
  }
}

/**
 * Validates that a string ID is non-empty.
 */
export function validateId(id: string, entityName: string): void {
  if (!id || id.trim().length === 0) {
    const error: ApiError = {
      code: "VALIDATION_ERROR",
      message: `Invalid ${entityName} ID: must be a non-empty string.`,
    };
    throw error;
  }
}
