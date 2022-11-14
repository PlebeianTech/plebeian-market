import { getApiBaseUrl } from "$lib/utils";

export async function load({ params }) {
    const { nym } = params;

    const userUrl = `${getApiBaseUrl()}api/users/${nym}`;
    const response = await fetch(userUrl)
    const user = await response.json()
    if (response.ok) {
        return {
            stallOwnerNym: nym,
            serverLoadedUser: user.user
        }
    }
    return {
        status: response.status,
        error: new Error("Could not fetch auction on the server")
    }
}
