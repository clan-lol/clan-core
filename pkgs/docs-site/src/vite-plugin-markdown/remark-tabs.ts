import { visit } from "unist-util-visit";
import type { Paragraph, Root, Text } from "mdast";
import type { ContainerDirectiveData } from "mdast-util-directive";

export default function remarkTabs() {
  return (tree: Root) => {
    visit(tree, (node) => {
      if (node.type !== "containerDirective" || node.name !== "tabs") {
        return;
      }

      const data: ContainerDirectiveData = {};
      node.data ||= data;
      data.hName = "div";
      data.hProperties = {
        className: "md-tabs",
      };
      let tabIndex = 0;
      const tabTitles: string[] = [];
      for (const [i, child] of node.children.entries()) {
        if (child.type !== "containerDirective" || child.name !== "tab") {
          continue;
        }
        let tabTitle: string;
        if (child.children?.[0]?.data?.directiveLabel) {
          const p = child.children.shift() as Paragraph;
          tabTitle = (p.children[0] as Text).value;
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
              className: "md-tabs-container",
            },
          },
          children: [
            {
              type: "paragraph",
              data: {
                hName: "div",
                hProperties: {
                  className: `md-tabs-tab ${tabIndex === 0 ? "is-active" : ""}`,
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
                  className: `md-tabs-content ${tabIndex === 0 ? "is-active" : ""}`,
                },
              },
              children: child.children,
            },
          ],
        };
        tabIndex += 1;
      }
      if (tabTitles.length === 1) {
        data.hProperties["className"] += " is-singleton";
      }
      // Add tab bar for when js is enabled
      node.children = [
        {
          type: "paragraph",
          data: {
            hName: "div",
            hProperties: {
              className: "md-tabs-bar",
            },
          },
          children: tabTitles.map((tabTitle, tabIndex) => ({
            type: "text",
            data: {
              hName: "div",
              hProperties: {
                className: `md-tabs-tab ${tabIndex === 0 ? "is-active" : ""}`,
              },
            },
            value: tabTitle,
          })),
        },
        ...node.children,
      ];
    });
  };
}
