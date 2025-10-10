export type Markdown = {
  content: string;
  frontmatter: Frontmatter;
  toc: Heading[];
};

export type Frontmatter = Record<string, any> & {
  title: string;
};

export type Heading = {
  id: string;
  content: string;
  children: Heading[];
};
