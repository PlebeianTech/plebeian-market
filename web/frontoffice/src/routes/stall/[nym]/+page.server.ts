import {getUser} from "../../../lib/services/api";

export async function load({ params }) {
    const { nym } = params;
    return await getUser(nym);
}
