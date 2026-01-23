import type { NavItemInput } from "$lib/models/docs";

export const navItems: NavItemInput[] = [
  {
    label: "Getting Started",
    items: ["/getting-started/add-machines"],
  },
  {
    label: "Reference",
    items: [
      {
        label: "Overview",
        slug: "/reference",
      },
      {
        label: "Options",
        autogenerate: { directory: "/reference/options" },
      },
    ],
  },
  {
    label: "Test",
    link: "/test",
  },
];
