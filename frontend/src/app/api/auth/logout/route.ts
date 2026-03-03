import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL!;

export async function POST(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;

  if (token) {
    await fetch(`${API_URL}/users/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {});
  }

  const response = NextResponse.json({ success: true });
  response.cookies.delete("access_token");
  response.cookies.delete("refresh_token");
  return response;
}
