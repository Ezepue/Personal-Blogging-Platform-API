import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL!;

export async function POST(req: NextRequest) {
  const body = await req.json();

  const form = new URLSearchParams();
  form.append("username", body.username);
  form.append("password", body.password);

  const res = await fetch(`${API_URL}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Login failed" }));
    return NextResponse.json(err, { status: res.status });
  }

  const data = await res.json();

  const response = NextResponse.json({ success: true });
  response.cookies.set("access_token", data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 30, // 30 minutes
  });
  if (data.refresh_token) {
    response.cookies.set("refresh_token", data.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });
  }
  return response;
}
