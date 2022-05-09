import type { Handle } from "@sveltejs/kit";

export async function handle({ event, resolve }): Promise<Handle> {
    const response = await resolve(event, {
      ssr: false,
      transformPage: ({ html }) => html
    });
   
    return response;
}
