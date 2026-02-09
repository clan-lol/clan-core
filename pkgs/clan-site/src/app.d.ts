import type { Article as DocsArticle } from "$lib/models/docs.ts";

declare global {
  // See https://svelte.dev/docs/kit/types#app.d.ts
  // for information about these interfaces
  namespace App {
    interface PageData {
      docsArticle?: DocsArticle;
    }
  }
}
