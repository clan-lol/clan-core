import { error } from "@sveltejs/kit";

const articles = Object.fromEntries(
  Object.entries(
    import.meta.glob<{
      content: string;
      frontmatter: Record<string, any>;
      toc: string;
    }>("../**/*.md"),
  ).map(([key, fn]) => [key.slice("../".length, -".md".length), fn]),
);

export async function load({ params }) {
  const path = params.path.endsWith("/")
    ? params.path.slice(0, -1)
    : params.path;
  const article = articles[path];
  if (!article) {
    error(404, "");
  }

  const { frontmatter, toc, content } = await article();
  return { frontmatter, toc, content };
}
