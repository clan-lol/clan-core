import { fromMarkdown } from "mdast-util-from-markdown";
import { matter } from "vfile-matter";
import type { Plugin } from "unified";
import type { Root } from "mdast";

const remarkParse: Plugin = function () {
  // eslint-disable-next-line no-this-in-exported-function
  this.parser = function parser(_document, file): Root {
    matter(file, { strip: true });
    return fromMarkdown(String(file));
  };
};
export default remarkParse;
