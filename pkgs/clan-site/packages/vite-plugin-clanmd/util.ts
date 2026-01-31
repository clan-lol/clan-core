import type { BlockContent, DefinitionContent, Paragraph } from "mdast";

export function isDirectiveParagraph(
  node: BlockContent | DefinitionContent | undefined,
): node is Paragraph {
  return node?.type === "paragraph" && node.data?.directiveLabel == null;
}

export type DeepReadOnly<T> = T extends object
  ? { readonly [P in keyof T]: DeepReadOnly<T[P]> }
  : T;
