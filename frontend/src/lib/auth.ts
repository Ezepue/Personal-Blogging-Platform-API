import { cookies } from "next/headers";

const API_URL = process.env.API_URL!;

export type User = {
  id: number;
  username: string;
  email: string;
  role: string;
  bio?: string | null;
  avatar_url?: string | null;
};

export async function getServerUser(): Promise<User | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  if (!token) return null;

  const res = await fetch(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!res.ok) return null;
  return res.json();
}
