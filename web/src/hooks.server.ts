import type { Handle } from "@sveltejs/kit";
import { getEntitiesAsync } from "$lib/services/api";
import { fromJson as auctionFromJson } from "$lib/types/auction";
import { fromJson as listingFromJson } from "$lib/types/listing";
import { generateSitemap } from "$lib/sitemap";
import { getBaseUrl } from "$lib/utils";

const ROBOTS_TXT = `User-agent: *
Allow: /
Disallow: /account
Sitemap: ${getBaseUrl()}sitemap.xml
`;

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }): Promise<Handle> {
    if (event.url.pathname === "/robots.txt") {
      return new Response(ROBOTS_TXT, {status: 200, headers: {"Content-Type": "text/plain"}});
    } else if (event.url.pathname === "/sitemap.xml") {
      const activeAuctions = await getEntitiesAsync({endpoint: 'auctions/active', responseField: 'auctions', fromJson: auctionFromJson}, null);
      const inactiveAuctions = await getEntitiesAsync({endpoint: 'auctions/inactive', responseField: 'auctions', fromJson: auctionFromJson}, null);
      const activeListings = await getEntitiesAsync({endpoint: 'listings/active', responseField: 'listings', fromJson: listingFromJson}, null);
      const inactiveListings = await getEntitiesAsync({endpoint: 'listings/inactive', responseField: 'listings', fromJson: listingFromJson}, null);
      return new Response(generateSitemap(["about", "faq"], activeAuctions, inactiveAuctions, activeListings, inactiveListings),
        {status: 200, headers: {"Content-Type": "application/xml"}});
    } else {
      return await resolve(event, {transformPageChunk: ({ html }) => html});
    }
}
