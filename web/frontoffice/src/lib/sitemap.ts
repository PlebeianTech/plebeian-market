import type { Auction } from "$lib/types/auction";
import type { Listing } from "$lib/types/listing";
import type { Item } from "$lib/types/item";
import { getBaseUrl } from "$lib/utils";

function getImages(item: Item) {
    let r = "";
    for (const media of item.media) {
        r += "<image:image>";
        r += `<image:loc>${media.url}</image:loc>`;
        r += "</image:image>";
    }
    return r;
}

function getUrl(url: string, date: Date | null, priority: number, changefreq: string, extra: string) {
    return `
    <url>
        <loc>${url}</loc>
        ${date ? "<lastmod>" + date.toISOString() + "</lastmod>" : ""}
        <priority>${priority}</priority>
        <changefreq>${changefreq}</changefreq>
        ${extra}
    </url>
    `;
}

export function generateSitemap(staticUrls: string[], activeAuctions: Auction[], inactiveAuctions: Auction[], activeListings: Listing[], inactiveListings: Listing[]) {
    const baseUrl = getBaseUrl();
    let sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">`;

    for (const url of staticUrls) {
        sitemap += getUrl(`${baseUrl}${url}`, null, 1, "weekly", "");
    }

    for (const auction of activeAuctions) {
        sitemap += getUrl(`${baseUrl}auctions/${auction.key}`, auction.start_date!, 1, "always", getImages(auction));
    }

    for (const auction of inactiveAuctions) {
        sitemap += getUrl(`${baseUrl}auctions/${auction.key}`, auction.end_date!, 0.1, "never", getImages(auction));
    }

    for (const listing of activeListings) {
        sitemap += getUrl(`${baseUrl}listings/${listing.key}`, listing.start_date!, 1, "always", getImages(listing));
    }

    for (const listing of inactiveListings) {
        sitemap += getUrl(`${baseUrl}listings/${listing.key}`, null, 0.1, "never", getImages(listing));
    }

    sitemap += `
</urlset>`;

    return sitemap;
}
