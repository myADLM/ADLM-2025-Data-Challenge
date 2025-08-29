import type { Route } from "./+types/home";
import { Assistant } from "./assistant";

export function loader() {
  return {};
}

export default function Home({ loaderData }: Route.ComponentProps) {
  return (
    <Assistant />
  );
}
