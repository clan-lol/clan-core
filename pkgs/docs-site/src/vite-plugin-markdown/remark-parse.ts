import type { Data, Processor } from "unified";
import { matter } from "vfile-matter";
import {
  type Extension as MarkdownExtension,
  fromMarkdown,
} from "mdast-util-from-markdown";
import type { Extension } from "micromark-util-types";

export default function remarkParse(this: Processor) {
  // eslint-disable-next-line @typescript-eslint/no-this-alias
  const self = this;
  this.parser = (_document, file) => {
    matter(file, { strip: true });
    // FIXME: fromMarkdown has a broken type definition, fix it and upstream
    const extensions = (self.data("micromarkExtensions" as unknown as Data) ||
      []) as unknown as Extension[];
    const mdastExtensions = (self.data(
      "fromMarkdownExtensions" as unknown as Data,
    ) || []) as unknown as MarkdownExtension[];
    return fromMarkdown(String(file), {
      extensions,
      mdastExtensions,
    });
  };
}
