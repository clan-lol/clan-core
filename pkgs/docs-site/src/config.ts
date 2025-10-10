import type { RawNavLink } from "$lib";

export default {
  navLinks: [
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
  ] as RawNavLink[],
};
