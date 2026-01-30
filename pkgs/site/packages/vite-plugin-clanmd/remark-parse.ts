import type { Plugin } from "unified";
import type { Root } from "mdast";
import { fromMarkdown } from "mdast-util-from-markdown";
import { matter } from "vfile-matter";

const remarkParse: Plugin = function () {
  const data = this.data.bind(this);
  this.parser = function parser(_document, file): Root {
    matter(file, { strip: true });
    // Adapted from https://github.com/remarkjs/remark/blob/main/packages/remark-parse/lib/index.js
    return fromMarkdown(String(file), {
      ...data("settings"),
      // These extensions are set by remark-gfm
      extensions: data("micromarkExtensions") ?? [],
      mdastExtensions: data("fromMarkdownExtensions") ?? [],
    });
  };
};
export default remarkParse;
