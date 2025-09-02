import type { RouteDefinition } from "@solidjs/router/dist/types";
import { Onboarding } from "@/src/routes/Onboarding/Onboarding";
import { Clan } from "@/src/routes/Clan/Clan";
import { Machine } from "@/src/routes/Machine/Machine";
import { Service } from "@/src/routes/Service/Service";

export const Routes: RouteDefinition[] = [
  {
    path: "/",
    component: Onboarding,
  },
  {
    path: "/clans",
    children: [
      {
        path: "/",
        component: () => (
          <h1>
            Clans (index) - (Doesnt really exist, just to keep the scene
            mounted)
          </h1>
        ),
      },
      {
        path: "/:clanURI",
        component: Clan,
        children: [
          {
            path: "/",
          },
          {
            path: "/machines/:machineName",
            component: Machine,
            children: [
              {
                path: "/",
              },
            ],
          },
          {
            path: "/services/:name/:id",
            component: Service,
          },
        ],
      },
    ],
  },
];
