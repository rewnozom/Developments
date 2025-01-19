import { remark } from 'remark';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkPrism from 'remark-prism';
import remarkToc from 'remark-toc';
import { visit } from 'unist-util-visit';

// Custom plugin för att hantera code blocks
const customCodePlugin = () => {
  return (tree: any) => {
    visit(tree, 'code', (node: any) => {
      node.data = {
        ...node.data,
        hProperties: {
          ...node.data?.hProperties,
          className: [`language-${node.lang || 'text'}`],
        },
      };
    });
  };
};

// Markdown processor med alla plugins
export const processor = remark()
  .use(remarkGfm)
  .use(remarkMath)
  .use(remarkPrism)
  .use(remarkToc)
  .use(customCodePlugin);

// Extrahera alla code blocks från markdown
export const extractCodeBlocks = (markdown: string) => {
  const codeBlocks: Array<{ language: string; code: string }> = [];
  const regex = /```(\w*)\n([\s\S]*?)```/g;
  let match;

  while ((match = regex.exec(markdown)) !== null) {
    codeBlocks.push({
      language: match[1] || 'text',
      code: match[2].trim(),
    });
  }

  return codeBlocks;
};

// Extrahera alla länkar från markdown
export const extractLinks = (markdown: string) => {
  const links: Array<{ text: string; url: string }> = [];
  const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;

  while ((match = regex.exec(markdown)) !== null) {
    links.push({
      text: match[1],
      url: match[2],
    });
  }

  return links;
};

// Generera table of contents
export const generateToc = (markdown: string) => {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  const toc: Array<{ level: number; text: string; slug: string }> = [];
  let match;

  while ((match = headingRegex.exec(markdown)) !== null) {
    toc.push({
      level: match[1].length,
      text: match[2],
      slug: slugify(match[2]),
    });
  }

  return toc;
};

// Helper för att skapa URL-vänliga slugs
const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

// Sanitize markdown för säker rendering
export const sanitizeMarkdown = (markdown: string): string => {
  return markdown
    .replace(/<(script|iframe|object|embed|form)/gi, '&lt;$1')
    .replace(/javascript:/gi, 'javascript：')
    .replace(/data:/gi, 'data：')
    .replace(/vbscript:/gi, 'vbscript：');
};

// Format markdown content
export const formatMarkdown = (markdown: string): string => {
  return markdown
    // Standardize line endings
    .replace(/\r\n/g, '\n')
    // Ensure consistent list markers
    .replace(/^[*+-]\s/gm, '- ')
    // Ensure consistent heading style (ATX)
    .replace(/^(.+)\n[=]+$/gm, '# $1')
    .replace(/^(.+)\n[-]+$/gm, '## $1')
    // Add empty lines around headings
    .replace(/^(#{1,6}\s.*?)\n(?!$)/gm, '$1\n\n')
    // Add empty lines around code blocks
    .replace(/^(```.*\n[\s\S]*?```)/gm, '\n$1\n')
    // Fix spacing in lists
    .replace(/^(\s*[-*+])\s+/gm, '$1 ');
};

// Parse markdown metadata (frontmatter)
export const parseMetadata = (markdown: string) => {
  const match = markdown.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return { content: markdown, metadata: {} };

  const metadataStr = match[1];
  const content = markdown.slice(match[0].length).trim();
  const metadata: Record<string, any> = {};

  metadataStr.split('\n').forEach(line => {
    const [key, ...values] = line.split(':');
    if (key && values.length) {
      metadata[key.trim()] = values.join(':').trim();
    }
  });

  return { content, metadata };
};
