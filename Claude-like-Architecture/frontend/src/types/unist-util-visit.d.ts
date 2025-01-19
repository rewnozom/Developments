declare module 'unist-util-visit' {
    import { Node } from 'unist';
  
    type Visitor<T extends Node> = (node: T, index: number | null, parent: T | null) => void;
  
    export default function visit<T extends Node>(
      tree: T,
      type: string,
      visitor: Visitor<T>
    ): void;
  }
  