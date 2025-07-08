import type { RouteDefinition } from "@solidjs/router/dist/types";
import { Onboarding } from "@/src/routes/Onboarding/Onboarding";
import { Clan } from "@/src/routes/Clan/Clan";

export const Routes: RouteDefinition[] = [
  {
    path: "/",
    component: Onboarding,
  },
  {
    path: "/clan/:clanURI",
    component: Clan,
  },
];
