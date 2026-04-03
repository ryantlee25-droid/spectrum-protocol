import { listPosts, getPost, createPost } from "../src/api/posts";
import { createTestToken } from "../src/api/auth";

const adminHeader = `Bearer ${createTestToken("u1", "admin")}`;
const memberHeader = `Bearer ${createTestToken("u2", "member")}`;
const guestHeader = `Bearer ${createTestToken("u3", "guest")}`;

describe("listPosts", () => {
  it("should return published posts for member", () => {
    const result = listPosts(memberHeader, { page: 1, limit: 10 });

    // Members see only published posts (2 out of 3)
    expect(result.data).toHaveLength(2);
    expect(result.data.every((p) => p.published)).toBe(true);
    expect(result.pagination.total).toBe(2);
  });

  it("should return all posts for admin", () => {
    const result = listPosts(adminHeader, { page: 1, limit: 10 });

    // Admins see all posts including drafts
    expect(result.data).toHaveLength(3);
    expect(result.pagination.total).toBe(3);
  });

  it("should paginate correctly", () => {
    const result = listPosts(adminHeader, { page: 1, limit: 2 });

    expect(result.data).toHaveLength(2);
    expect(result.pagination.totalPages).toBe(2);
  });

  it("should throw for unauthenticated request", () => {
    expect(() => listPosts(undefined, { page: 1, limit: 10 })).toThrow();
  });

  it("should throw for invalid pagination", () => {
    expect(() => listPosts(adminHeader, { page: -1, limit: 10 })).toThrow();
    expect(() => listPosts(adminHeader, { page: 1, limit: 101 })).toThrow();
  });
});

describe("getPost", () => {
  it("should return a published post for any role", () => {
    const post = getPost(guestHeader, "p1");

    expect(post.id).toBe("p1");
    expect(post.title).toBe("Getting Started");
  });

  it("should return an unpublished post for admin", () => {
    const post = getPost(adminHeader, "p3");

    expect(post.id).toBe("p3");
    expect(post.published).toBe(false);
  });

  it("should throw for non-admin accessing unpublished post", () => {
    expect(() => getPost(memberHeader, "p3")).toThrow();
    try {
      getPost(memberHeader, "p3");
    } catch (err: any) {
      expect(err.code).toBe("FORBIDDEN");
    }
  });

  it("should throw for non-existent post", () => {
    expect(() => getPost(adminHeader, "p999")).toThrow();
    try {
      getPost(adminHeader, "p999");
    } catch (err: any) {
      expect(err.code).toBe("NOT_FOUND");
    }
  });
});

describe("createPost", () => {
  it("should allow member to create a post", () => {
    const post = createPost(memberHeader, {
      title: "New Post",
      body: "Content here",
      tags: ["test"],
    });

    expect(post.title).toBe("New Post");
    expect(post.authorId).toBe("u2");
    expect(post.published).toBe(false);
  });

  it("should prevent guest from creating a post", () => {
    expect(() =>
      createPost(guestHeader, {
        title: "Guest Post",
        body: "Should fail",
        tags: [],
      })
    ).toThrow();
    try {
      createPost(guestHeader, {
        title: "Guest Post",
        body: "Should fail",
        tags: [],
      });
    } catch (err: any) {
      expect(err.code).toBe("FORBIDDEN");
    }
  });
});
