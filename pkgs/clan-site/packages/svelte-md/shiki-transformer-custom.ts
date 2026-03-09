import type { Element } from "hast";
import type { ShikiTransformer } from "shiki";

export default function transformerCustom({
  minLines,
}: {
  readonly minLines: number;
}): ShikiTransformer {
  return {
    pre(pre): void {
      const code = pre.children.find(
        (node) => node.type === "element" && node.tagName === "code",
      ) as Element | undefined;
      if (!code) {
        return;
      }

      let lines = 0;
      for (const node of code.children) {
        if (node.type === "element" && node.properties.class === "line") {
          lines += 1;
        }
      }

      if (lines >= minLines) {
        this.addClassToHast(pre, "line-numbers");
      }

      code.children = [
        {
          type: "element",
          tagName: "span",
          properties: {
            class: "code",
          },
          children: code.children,
        },
      ];

      // eslint-disable-next-line no-underscore-dangle
      const meta = this.options.meta?.__raw;
      if (!meta) {
        return;
      }
      const result = /(?:^|\s)\[(?<title>(?:\\]|[^\]])+)\](?:$|\s)/.exec(meta);
      const title = result?.groups?.["title"];
      if (!title) {
        return;
      }

      pre.children.unshift({
        type: "element",
        tagName: "span",
        properties: {
          class: "title",
        },
        children: [{ type: "text", value: title }],
      });
    },
  };
}
