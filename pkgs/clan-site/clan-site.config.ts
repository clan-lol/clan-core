import pathutil from "node:path";
import process from "node:process";

export interface Config {
  ver: string;
  docs: {
    dir: string;
    base: DocsPath;
    searchResultLimit: number;
    minLineNumberLines: number;
    maxTocExtractionDepth: number;
    codeLightTheme: string;
    codeDarkTheme: string;
    indexArticleTitle: string;
    nav: NavItem[];
  };
}

export type Path = `/${string}`;
export type DocsPath = `/docs/${string}`;

export type NavItem =
  | Path
  | {
      readonly label: string;
      readonly items: readonly NavItem[];
      readonly collapsed?: boolean;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly auto: Path;
      readonly collapsed?: boolean;
      readonly badge?: Badge;
    }
  | {
      readonly label?: string;
      readonly slug: Path;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly path: Path;
      readonly badge?: Badge;
    }
  | {
      readonly label: string;
      readonly url: string;
      readonly badge?: Badge;
    };

export type Badge =
  | string
  | {
      readonly text: string;
      readonly variant: "caution" | "normal";
    };

const ver = process.env["SITE_VER"] || "unstable";
const config: Config = {
  ver,
  docs: {
    dir: pathutil.normalize("src/docs"),
    base: `/docs/${ver}`,
    searchResultLimit: 5,
    minLineNumberLines: 4,
    maxTocExtractionDepth: 3,
    codeLightTheme: "catppuccin-latte",
    codeDarkTheme: "catppuccin-macchiato",
    indexArticleTitle: "Sovereign Infrastructure by Design",
    nav: [
      {
        label: "Getting Started",
        items: [
          "/",
          "/getting-started/creating-your-first-clan",
          "/getting-started/add-machines",
          "/getting-started/add-users",
          "/getting-started/add-services",
          "/getting-started/prepare-physical-machines",
          "/getting-started/prepare-virtual-machines",
          "/getting-started/configure-disk",
          "/getting-started/deployment-phase",
          "/getting-started/update-machines",
          "/getting-started/whats-next",
        ],
      },
      {
        label: "Gudies",
        items: ["/guides/inventory/inventory"],
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
            auto: "/reference/options",
          },
        ],
      },
      {
        label: "Services",
        items: ["/services/definition"],
      },
      {
        label: "Test",
        path: "/test",
      },
    ],
  },
};

export default config;
