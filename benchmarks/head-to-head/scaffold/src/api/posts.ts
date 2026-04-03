import { Post, PaginationParams, PaginatedResponse, ApiError } from "../types";
import { config } from "../config";
import { authMiddleware, AuthContext } from "./auth";
import { validatePagination } from "../utils/validate";
import { log } from "../utils/logger";

/**
 * In-memory post store for the scaffold.
 * Seeded with sample data for tests.
 */
const posts: Post[] = [
  {
    id: "p1",
    title: "Getting Started",
    body: "Welcome to the platform.",
    authorId: "u1",
    tags: ["intro", "guide"],
    published: true,
    createdAt: new Date("2024-01-15"),
    updatedAt: new Date("2024-01-15"),
  },
  {
    id: "p2",
    title: "Advanced Tips",
    body: "Here are some advanced tips.",
    authorId: "u2",
    tags: ["tips", "advanced"],
    published: true,
    createdAt: new Date("2024-02-20"),
    updatedAt: new Date("2024-03-01"),
  },
  {
    id: "p3",
    title: "Draft Post",
    body: "This is a draft.",
    authorId: "u1",
    tags: ["draft"],
    published: false,
    createdAt: new Date("2024-03-10"),
    updatedAt: new Date("2024-03-10"),
  },
];

/**
 * List posts with pagination.
 * Requires auth — any authenticated role can list published posts.
 * Admins can see unpublished posts too.
 */
export function listPosts(
  authHeader: string | undefined,
  params: PaginationParams
): PaginatedResponse<Post> {
  const auth: AuthContext = authMiddleware(authHeader);
  log("info", `User ${auth.userId} listing posts`);

  validatePagination(params.page, params.limit);

  const visiblePosts =
    auth.role === "admin"
      ? posts
      : posts.filter((p) => p.published);

  const start = (params.page - 1) * params.limit;
  const end = start + params.limit;
  const pageData = visiblePosts.slice(start, end);

  return {
    data: pageData,
    pagination: {
      page: params.page,
      limit: params.limit,
      total: visiblePosts.length,
      totalPages: Math.ceil(visiblePosts.length / params.limit),
    },
  };
}

/**
 * Get a single post by ID.
 * Requires auth — non-admins can only see published posts.
 */
export function getPost(
  authHeader: string | undefined,
  postId: string
): Post {
  const auth: AuthContext = authMiddleware(authHeader);
  log("info", `User ${auth.userId} fetching post ${postId}`);

  const post = posts.find((p) => p.id === postId);
  if (!post) {
    const error: ApiError = {
      code: "NOT_FOUND",
      message: `Post ${postId} not found`,
    };
    throw error;
  }

  if (!post.published && auth.role !== "admin") {
    const error: ApiError = {
      code: "FORBIDDEN",
      message: "Cannot access unpublished post",
    };
    throw error;
  }

  return post;
}

/**
 * Create a new post.
 * Requires auth — only admins and members can create posts.
 */
export function createPost(
  authHeader: string | undefined,
  data: { title: string; body: string; tags: string[] }
): Post {
  const auth: AuthContext = authMiddleware(authHeader);
  log("info", `User ${auth.userId} creating post`);

  if (auth.role === "guest") {
    const error: ApiError = {
      code: "FORBIDDEN",
      message: "Guests cannot create posts",
    };
    throw error;
  }

  const newPost: Post = {
    id: `p${posts.length + 1}`,
    title: data.title,
    body: data.body,
    authorId: auth.userId,
    tags: data.tags,
    published: false,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  posts.push(newPost);
  return newPost;
}
