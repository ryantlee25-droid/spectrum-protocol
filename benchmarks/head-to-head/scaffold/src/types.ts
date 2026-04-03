/**
 * Core domain types for the scaffold API.
 * Task 1 will rename `User` to `Account` across all files.
 */

export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "member" | "guest";
  createdAt: Date;
}

export interface Post {
  id: string;
  title: string;
  body: string;
  authorId: string;
  tags: string[];
  published: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
