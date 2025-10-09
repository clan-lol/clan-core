export type Markdown = {
  content: string;
  frontmatter: Record<string, any> & {
    title: string;
  };
  toc: Heading[];
};

export type Heading = {
  id: string;
  content: string;
  children: Heading[];
};
