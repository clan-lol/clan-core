const articles = import.meta.glob("./**/*.md");

export function load() {
  const paths = Object.keys(articles).map((key) =>
    key.slice("./".length, -".md".length),
  );
  return { paths };
}
