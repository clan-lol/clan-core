import type { RouteDefinition } from "@solidjs/router/dist/types";
import { Onboarding } from "@/src/routes/Onboarding/Onboarding";
import { Clan } from "@/src/routes/Clan/Clan";

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
        children: [
          {
            path: "/",
            component: Clan,
          },
          {
            path: "/machines",
            children: [
              {
                path: "/",
                component: () => <h1>Machines (Index)</h1>,
              },
              {
                path: "/:machineID",
                component: (props) => (
                  <h1>Machine ID: {props.params.machineID}</h1>
                ),
              },
            ],
          },
        ],
      },
    ],
  },
];
