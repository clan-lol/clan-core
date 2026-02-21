import type { BlockContent, DefinitionContent, Paragraph } from "mdast";

export function isParagraphDirective(
  node: BlockContent | DefinitionContent | undefined,
): node is Paragraph {
  return (
    node?.type === "paragraph" && typeof node.data?.directiveLabel === "boolean"
  );
}
