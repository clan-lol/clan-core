import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import { matter } from "vfile-matter";
import { unified } from "unified";
import { VFile } from "vfile";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import { toc } from "mdast-util-toc";
import type { Nodes } from "mdast";

export default defineConfig({
  plugins: [
    sveltekit(),
    {
      name: "markdown-loader",
      async transform(code, id) {
        if (id.slice(-3) !== ".md") return;

        // TODO: move VFile into unified
        const file = new VFile(code);
        matter(file, { strip: true });
        const html = await unified()
          .use(remarkParse)
          .use(remarkRehype)
          .use(rehypeStringify)
          .process(String(code));

        const parsed = await unified()
          .use(remarkParse)
          .use(() => (tree) => {
            const result = toc(tree as Nodes);
            return result.map;
          })
          .use(remarkRehype)
          .use(rehypeStringify)
          .process(file);

        console.log("toc", parsed);
        return `
export default ${JSON.stringify(String(html))};
export const frontmatter = ${JSON.stringify(file.data.matter)};
export const toc = ${JSON.stringify(String(parsed))};`;
      },
    },
  ],
});
