import {getAuction} from "../../../lib/services/api";

export async function load({ params }) {
    const { key } = params;
    return await getAuction(key);
}
