import type { BlockContent, DefinitionContent, Paragraph } from "mdast";

export function isDirectiveParagraph(
  // eslint-disable-next-line @typescript-eslint/prefer-readonly-parameter-types
  node: BlockContent | DefinitionContent | undefined,
): node is Paragraph {
  return node?.type === "paragraph" && node.data?.directiveLabel == null;
}

export type DeepReadOnly<T> = T extends object
  ? { readonly [P in keyof T]: DeepReadOnly<T[P]> }
  : T;
