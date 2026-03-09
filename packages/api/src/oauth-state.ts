import { createHmac, timingSafeEqual } from "node:crypto";

type OAuthStatePayload = {
  workspaceId: string;
  shopId: string;
  provider: string;
  providerId?: string;
  username?: string;
};

function base64UrlEncode(value: string): string {
  return Buffer.from(value, "utf8").toString("base64url");
}

function base64UrlDecode(value: string): string {
  return Buffer.from(value, "base64url").toString("utf8");
}

function sign(secret: string, payload: string): string {
  return createHmac("sha256", secret).update(payload).digest("base64url");
}

export function encodeOAuthState(
  secret: string,
  payload: OAuthStatePayload,
): string {
  const encodedPayload = base64UrlEncode(JSON.stringify(payload));
  const signature = sign(secret, encodedPayload);

  return `${encodedPayload}.${signature}`;
}

export function decodeOAuthState(
  secret: string,
  state: string,
): OAuthStatePayload {
  const [encodedPayload, signature] = state.split(".");

  if (!encodedPayload || !signature) {
    throw new Error("OAuth state has invalid format.");
  }

  const expected = sign(secret, encodedPayload);

  if (
    !timingSafeEqual(
      Buffer.from(signature, "utf8"),
      Buffer.from(expected, "utf8"),
    )
  ) {
    throw new Error("OAuth state signature mismatch.");
  }

  return JSON.parse(base64UrlDecode(encodedPayload)) as OAuthStatePayload;
}

export type { OAuthStatePayload };
