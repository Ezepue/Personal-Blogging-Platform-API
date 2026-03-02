export type User = {
  id: number;
  username: string;
  email: string;
  role: string;
  bio?: string | null;
  avatar_url?: string | null;
};
