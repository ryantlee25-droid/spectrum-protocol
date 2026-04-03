import { authMiddleware, createTestToken, createAuthError } from "../src/api/auth";

describe("authMiddleware", () => {
  it("should authenticate a valid admin token", () => {
    const token = createTestToken("u1", "admin");
    const header = `Bearer ${token}`;

    const ctx = authMiddleware(header);

    expect(ctx.userId).toBe("u1");
    expect(ctx.role).toBe("admin");
  });

  it("should authenticate a valid member token", () => {
    const token = createTestToken("u2", "member");
    const header = `Bearer ${token}`;

    const ctx = authMiddleware(header);

    expect(ctx.userId).toBe("u2");
    expect(ctx.role).toBe("member");
  });

  it("should throw for missing header", () => {
    expect(() => authMiddleware(undefined)).toThrow();
    try {
      authMiddleware(undefined);
    } catch (err: any) {
      expect(err.code).toBe("AUTH_ERROR");
      expect(err.message).toContain("Missing");
    }
  });

  it("should throw for non-Bearer header", () => {
    expect(() => authMiddleware("Basic abc123")).toThrow();
    try {
      authMiddleware("Basic abc123");
    } catch (err: any) {
      expect(err.code).toBe("AUTH_ERROR");
      expect(err.message).toContain("Bearer");
    }
  });

  it("should throw for invalid base64 token", () => {
    expect(() => authMiddleware("Bearer not-valid-base64!!!")).toThrow();
    try {
      authMiddleware("Bearer not-valid-base64!!!");
    } catch (err: any) {
      expect(err.code).toBe("AUTH_ERROR");
    }
  });

  it("should throw for token missing userId", () => {
    const token = Buffer.from(JSON.stringify({ role: "admin" })).toString("base64");
    expect(() => authMiddleware(`Bearer ${token}`)).toThrow();
    try {
      authMiddleware(`Bearer ${token}`);
    } catch (err: any) {
      expect(err.code).toBe("AUTH_ERROR");
      expect(err.message).toContain("Malformed");
    }
  });
});

describe("createAuthError", () => {
  it("should create a properly shaped error", () => {
    const err = createAuthError("test message");
    expect(err.code).toBe("AUTH_ERROR");
    expect(err.message).toBe("test message");
  });
});
