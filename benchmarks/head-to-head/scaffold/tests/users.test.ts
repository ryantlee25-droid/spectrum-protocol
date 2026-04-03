import { listUsers, getUser } from "../src/api/users";
import { createTestToken } from "../src/api/auth";

const adminHeader = `Bearer ${createTestToken("u1", "admin")}`;
const memberHeader = `Bearer ${createTestToken("u2", "member")}`;

describe("listUsers", () => {
  it("should return paginated users for authenticated request", () => {
    const result = listUsers(adminHeader, { page: 1, limit: 10 });

    expect(result.data).toHaveLength(3);
    expect(result.pagination.page).toBe(1);
    expect(result.pagination.limit).toBe(10);
    expect(result.pagination.total).toBe(3);
    expect(result.pagination.totalPages).toBe(1);
  });

  it("should paginate correctly with small limit", () => {
    const result = listUsers(adminHeader, { page: 1, limit: 2 });

    expect(result.data).toHaveLength(2);
    expect(result.pagination.total).toBe(3);
    expect(result.pagination.totalPages).toBe(2);
  });

  it("should return second page correctly", () => {
    const result = listUsers(adminHeader, { page: 2, limit: 2 });

    expect(result.data).toHaveLength(1);
    expect(result.data[0].id).toBe("u3");
  });

  it("should accept limit of 100 (max allowed)", () => {
    const result = listUsers(adminHeader, { page: 1, limit: 100 });

    expect(result.data).toHaveLength(3);
    expect(result.pagination.limit).toBe(100);
  });

  it("should throw for unauthenticated request", () => {
    expect(() => listUsers(undefined, { page: 1, limit: 10 })).toThrow();
  });

  it("should throw for invalid pagination", () => {
    expect(() => listUsers(adminHeader, { page: 0, limit: 10 })).toThrow();
    expect(() => listUsers(adminHeader, { page: 1, limit: 0 })).toThrow();
    expect(() => listUsers(adminHeader, { page: 1, limit: 101 })).toThrow();
  });
});

describe("getUser", () => {
  it("should return a user by ID", () => {
    const user = getUser(adminHeader, "u1");

    expect(user.id).toBe("u1");
    expect(user.name).toBe("Alice Admin");
    expect(user.email).toBe("alice@example.com");
  });

  it("should throw for non-existent user", () => {
    expect(() => getUser(adminHeader, "u999")).toThrow();
    try {
      getUser(adminHeader, "u999");
    } catch (err: any) {
      expect(err.code).toBe("NOT_FOUND");
    }
  });

  it("should throw for unauthenticated request", () => {
    expect(() => getUser(undefined, "u1")).toThrow();
  });
});
