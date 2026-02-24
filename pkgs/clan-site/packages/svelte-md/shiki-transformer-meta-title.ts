import type { ShikiTransformer } from "shiki";

export default function transformerMetaTitle(): ShikiTransformer {
  return {
    pre(pre) {
      // eslint-disable-next-line no-underscore-dangle
      const meta = this.options.meta?.__raw;
      if (!meta) {
        return;
      }
      // TODO: support escaping like [foo/\[...path]]
      const result = /\[(?<title>[^\]]+)\]/.exec(meta);
      const title = result?.groups?.["title"];
      if (!title) {
        return;
      }

      pre.children = [
        {
          type: "element",
          tagName: "div",
          properties: {
            class: "title",
          },
          children: [{ type: "text", value: title }],
        },
        ...pre.children,
      ];
    },
  };
}
