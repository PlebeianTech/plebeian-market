import type { Handle } from "@sveltejs/kit";

export async function handle({ event, resolve }): Promise<Handle> {
    // use server side render on home, about, faq and auctions
    const response = await resolve(event, {
      ssr: true, //["/", "/about", "/faq"].includes(event.url.pathname) || event.url.pathname.includes("/auctions") ? true : false,
      transformPage: ({ html }) => html
    });
    return response;
}
