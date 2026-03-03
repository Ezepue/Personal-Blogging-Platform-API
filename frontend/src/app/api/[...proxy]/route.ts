import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function handler(
  req: NextRequest,
  { params }: { params: { proxy: string[] } }
) {
  const token = req.cookies.get("access_token")?.value;
  const path = params.proxy.join("/");
  const url = `${API_URL}/${path}${req.nextUrl.search}`;

  const contentType = req.headers.get("content-type") ?? "";
  const headers: Record<string, string> = {};
  if (contentType) headers["Content-Type"] = contentType;
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let body: BodyInit | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    // Pass through form data or JSON as-is
    body = await req.blob();
  }

  const res = await fetch(url, {
    method: req.method,
    headers,
    body,
  });

  const responseContentType = res.headers.get("content-type") ?? "application/json";
  const data = await res.arrayBuffer();

  return new NextResponse(data, {
    status: res.status,
    headers: { "Content-Type": responseContentType },
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
export const PATCH = handler;
