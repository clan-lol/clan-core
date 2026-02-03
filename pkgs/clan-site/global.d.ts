// TODO: fina a way to generate the Config type automatically
// from clan-site.config.ts
declare module "$config" {
  export interface Config {
    ver: string;
    docs: {
      searchResultLimit: number;
      minLineNumberLines: number;
      maxTocExtractionDepth: number;
      codeLightTheme: string;
      codeDarkTheme: string;
      nav: NavItem[];
    };
  }
  const config: Config;
  export default config;
  export type Path = `/${string}`;
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
        readonly autogenerate: { readonly directory: Path };
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
        readonly link: Path;
        readonly badge?: Badge;
      };

  export type Badge =
    | string
    | {
        readonly text: string;
        readonly variant: "caution" | "normal";
      };
}
