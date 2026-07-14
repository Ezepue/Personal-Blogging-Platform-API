import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

// Exchange the httpOnly access-token cookie for a short-lived, single-purpose
// WebSocket ticket. The long-lived access token is never exposed to client JS.
export async function GET(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const res = await fetch(`${API_URL}/users/ws-ticket`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!res.ok) {
    return NextResponse.json({ error: "Could not obtain ticket" }, { status: res.status });
  }

  const data = (await res.json()) as { ticket: string };
  return NextResponse.json({ token: data.ticket });
}
