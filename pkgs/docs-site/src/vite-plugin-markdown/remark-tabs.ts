import type { ContainerDirectiveData } from "mdast-util-directive";
import { isDirectiveParagraph } from "./util.ts";
import type { Plugin } from "unified";
import type { Root } from "mdast";
import { visit } from "unist-util-visit";

const remarkTabs: Plugin<[], Root> = function () {
  return (tree) => {
    visit(tree, (node) => {
      if (node.type !== "containerDirective" || node.name !== "tabs") {
        return;
      }

      const data: ContainerDirectiveData = {};
      node.data ??= data;
      data.hName = "div";
      data.hProperties = {
        class: "md-tabs",
      };
      let tabIndex = 0;
      const tabTitles: string[] = [];
      for (const [i, child] of node.children.entries()) {
        if (child.type !== "containerDirective" || child.name !== "tab") {
          continue;
        }
        let tabTitle: string;
        const p = child.children?.[0];
        if (isDirectiveParagraph(p) && p.children?.[0]?.type === "text") {
          child.children.shift();
          tabTitle = p.children[0].value;
        } else {
          tabTitle = "(empty)";
        }
        tabTitles.push(tabTitle);
        node.children[i] = {
          type: "containerDirective",
          name: "",
          data: {
            hName: "div",
            hProperties: {
              class: "md-tabs-container",
            },
          },
          children: [
            {
              type: "paragraph",
              data: {
                hName: "div",
                hProperties: {
                  class: `md-tabs-tab ${tabIndex === 0 ? "is-active" : ""}`,
                },
              },
              children: [{ type: "text", value: tabTitle }],
            },
            {
              type: "containerDirective",
              name: "",
              data: {
                hName: "div",
                hProperties: {
                  class: `md-tabs-content ${tabIndex === 0 ? "is-active" : ""}`,
                },
              },
              children: child.children,
            },
          ],
        };
        tabIndex += 1;
      }
      if (tabTitles.length === 1) {
        data.hProperties.class += " is-singleton";
      }
      // Add tab bar for when js is enabled
      node.children = [
        {
          type: "paragraph",
          data: {
            hName: "div",
            hProperties: {
              class: "md-tabs-bar",
            },
          },
          children: tabTitles.map((tabTitle, tabIndex) => ({
            type: "text",
            data: {
              hName: "div",
              hProperties: {
                class: `md-tabs-tab ${tabIndex === 0 ? "is-active" : ""}`,
              },
            },
            value: tabTitle,
          })),
        },
        ...node.children,
      ];
    });
  };
};
export default remarkTabs;
