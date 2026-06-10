import type {
  Code,
  Definition,
  Html,
  Image,
  InlineCode,
  Link,
  Root,
  Text,
} from "mdast";
import type { Plugin } from "unified";
import type { VFile } from "vfile";
import { visit } from "unist-util-visit";

type VariableNode = Code | Html | InlineCode | Text;
type UrlNode = Definition | Image | Link;

interface Options {
  readonly variables: Readonly<Record<string, string>>;
}

const variablePattern =
  /\{\{(?<escape>!)?\s+(?<name>[A-Za-z][A-Za-z0-9_-]*)\s+\}\}/g;

const remarkTemplateVariables: Plugin<[Options], Root> = function ({
  variables,
}) {
  return (tree, file) => {
    visit(tree, ["code", "html", "inlineCode", "text"] as const, (node) => {
      const variableNode = node as VariableNode;
      variableNode.value = replaceVariables(
        variableNode.value,
        variables,
        file,
      );
    });

    visit(tree, ["definition", "image", "link"] as const, (node) => {
      const urlNode = node as UrlNode;
      urlNode.url = replaceVariables(urlNode.url, variables, file);
    });
  };
};

function replaceVariables(
  value: string,
  variables: Readonly<Record<string, string>>,
  file: VFile,
): string {
  return value.replaceAll(variablePattern, (match, escape, name: string) => {
    if (escape === "!") {
      return `{{ ${name} }}`;
    }

    const replacement = variables[name];
    if (replacement === undefined) {
      file.fail(`Unknown markdown template variable: ${match}`);
    }
    return replacement;
  });
}

export default remarkTemplateVariables;
