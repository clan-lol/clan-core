import type { Processor } from "unified";
import { matter } from "vfile-matter";
import { fromMarkdown } from "mdast-util-from-markdown";

export default function remarkParse(this: Processor) {
  this.parser = (document, file) => {
    matter(file, { strip: true });
    return fromMarkdown(String(file));
  };
}
