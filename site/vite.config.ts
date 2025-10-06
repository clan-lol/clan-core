import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import { matter } from "vfile-matter";
import { unified } from "unified";
import { VFile } from "vfile";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";

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
          .process(String(file));

        return `
export default ${JSON.stringify(String(html))};
export const frontmatter = ${JSON.stringify(file.data.matter)};`;
      },
    },
  ],
});
