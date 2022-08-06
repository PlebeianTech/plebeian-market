import type { Handle } from "@sveltejs/kit";

export async function handle({ event, resolve }): Promise<Handle> {
    // use server side render
    const response = await resolve(event, {
      ssr: true,
      transformPage: ({ html }) => html
    });
    return response;
}
