import type { NavLink } from "./utils";

export const navLinks: NavLink[] = [
  {
    label: "Getting Started",
    items: ["getting-started/add-machines"],
  },
  {
    label: "Reference",
    items: [
      {
        label: "Overview",
        slug: "reference/overview",
      },
      {
        label: "Options",
        autogenerate: { directory: "reference/options" },
      },
    ],
  },
];
