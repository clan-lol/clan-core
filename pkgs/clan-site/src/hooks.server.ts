import type { Handle } from "@sveltejs/kit";

export const handle: Handle = async ({ event, resolve }) =>
  await resolve(event, {
    // Refer to kit.paths.assets in svelte.config.ts on what this is for
    transformPageChunk({ html }) {
      return html.replaceAll(
        "https://36f875d1-c51e-47f5-83cd-3ff35490163f",
        "",
      );
    },
  });
