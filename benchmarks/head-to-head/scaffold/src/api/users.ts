import { User, PaginationParams, PaginatedResponse, ApiError } from "../types";
import { config } from "../config";
import { authMiddleware, AuthContext } from "./auth";
import { validatePagination } from "../utils/validate";
import { log } from "../utils/logger";

/**
 * In-memory user store for the scaffold.
 * Seeded with sample data for tests.
 */
const users: User[] = [
  {
    id: "u1",
    email: "alice@example.com",
    name: "Alice Admin",
    role: "admin",
    createdAt: new Date("2024-01-01"),
  },
  {
    id: "u2",
    email: "bob@example.com",
    name: "Bob Member",
    role: "member",
    createdAt: new Date("2024-02-01"),
  },
  {
    id: "u3",
    email: "carol@example.com",
    name: "Carol Guest",
    role: "guest",
    createdAt: new Date("2024-03-01"),
  },
];

/**
 * List users with pagination.
 * Requires auth — any authenticated role can list users.
 */
export function listUsers(
  authHeader: string | undefined,
  params: PaginationParams
): PaginatedResponse<User> {
  const auth: AuthContext = authMiddleware(authHeader);
  log("info", `User ${auth.userId} listing users`);

  validatePagination(params.page, params.limit);

  const start = (params.page - 1) * params.limit;
  const end = start + params.limit;
  const pageData = users.slice(start, end);

  return {
    data: pageData,
    pagination: {
      page: params.page,
      limit: params.limit,
      total: users.length,
      totalPages: Math.ceil(users.length / params.limit),
    },
  };
}

/**
 * Get a single user by ID.
 * Requires auth — any authenticated role can view a user.
 */
export function getUser(
  authHeader: string | undefined,
  userId: string
): User {
  const auth: AuthContext = authMiddleware(authHeader);
  log("info", `User ${auth.userId} fetching user ${userId}`);

  const user = users.find((u) => u.id === userId);
  if (!user) {
    const error: ApiError = {
      code: "NOT_FOUND",
      message: `User ${userId} not found`,
    };
    throw error;
  }

  return user;
}
