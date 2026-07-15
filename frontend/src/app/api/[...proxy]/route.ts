import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

const ACCESS_COOKIE = "access_token";
const REFRESH_COOKIE = "refresh_token";

type Upstream = { status: number; body: ArrayBuffer; contentType: string };

async function callUpstream(
  method: string,
  url: string,
  token: string | undefined,
  contentType: string,
  body: BodyInit | undefined,
): Promise<Upstream> {
  const headers: Record<string, string> = {};
  if (contentType) headers["Content-Type"] = contentType;
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { method, headers, body, cache: "no-store" });
  return {
    status: res.status,
    body: await res.arrayBuffer(),
    contentType: res.headers.get("content-type") ?? "application/json",
  };
}

async function handler(req: NextRequest, { params }: { params: { proxy: string[] } }) {
  const accessToken = req.cookies.get(ACCESS_COOKIE)?.value;
  const refreshToken = req.cookies.get(REFRESH_COOKIE)?.value;
  const path = params.proxy.join("/");
  const url = `${API_URL}/${path}${req.nextUrl.search}`;
  const contentType = req.headers.get("content-type") ?? "";

  // Buffer the body so we can safely replay the request after a token refresh.
  const rawBody =
    req.method !== "GET" && req.method !== "HEAD" ? await req.arrayBuffer() : undefined;
  const body = rawBody && rawBody.byteLength ? rawBody : undefined;

  let upstream = await callUpstream(req.method, url, accessToken, contentType, body);
  let refreshedAccess: string | undefined;

  // Transparent refresh: on a 401 with a live refresh token, mint a new access
  // token and replay the original request once. Keeps sessions alive across the
  // 30-minute access-token expiry without a visible logout.
  if (upstream.status === 401 && refreshToken) {
    const refreshRes = await fetch(`${API_URL}/users/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });
    if (refreshRes.ok) {
      try {
        const data = (await refreshRes.json()) as { access_token: string };
        if (data?.access_token) {
          refreshedAccess = data.access_token;
          upstream = await callUpstream(req.method, url, refreshedAccess, contentType, body);
        }
      } catch {
        // Malformed refresh response — fall through with the original 401.
      }
    }
  }

  const response = new NextResponse(upstream.body, {
    status: upstream.status,
    headers: { "Content-Type": upstream.contentType },
  });

  if (refreshedAccess) {
    response.cookies.set(ACCESS_COOKIE, refreshedAccess, {
      httpOnly: true,
      sameSite: "strict",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 30 * 60,
    });
  }
  return response;
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
