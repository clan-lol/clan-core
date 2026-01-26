import type { BlockContent, DefinitionContent, Paragraph } from "mdast";

export function isDirectiveParagraph(
  node: BlockContent | DefinitionContent | undefined,
): node is Paragraph {
  return node?.type === "paragraph" && node?.data?.directiveLabel == null;
}
