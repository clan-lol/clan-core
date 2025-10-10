import type { RawNavItem } from "$lib";

export default {
  navItems: [
    {
      label: "Getting Started",
      items: ["/getting-started/add-machines"],
    },
    {
      label: "Reference",
      items: [
        {
          label: "Overview",
          slug: "/reference/overview",
        },
        {
          label: "Options",
          autogenerate: { directory: "/reference/options" },
        },
      ],
    },
    {
      label: "Test",
      link: "/test/overview",
    },
  ] as RawNavItem[],
};
