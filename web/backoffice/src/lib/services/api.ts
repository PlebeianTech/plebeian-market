import { error } from '@sveltejs/kit';
import { Error as ErrorStore, AuthRequired, AuthBehavior } from "$lib/stores";
import type { IEntity, IEntityBase } from "$lib/types/base";
import type { AddedMedia } from "$lib/types/item";
import { type Order, fromJson as orderFromJson } from "$lib/types/order";
import { ExternalAccountProvider, type User, fromJson as userFromJson } from "$lib/types/user";
import { getApiBaseUrl, logout } from "$lib/utils";

export class ErrorHandler {
    setError: boolean;
    onError: (response: Response) => void;

    public constructor(setError: boolean = true, onError: (response: Response) => void = () => {}) {
        this.setError = setError;
        this.onError = onError;
    }

    public handle(response) {
        if (this.setError) {
            response.json().then(data => { ErrorStore.set(data.message); });
        }

        this.onError(response);
    }
}

function getFetchOptions(method: string, tokenValue: string | null, body: any | null, contentType: string | null) {
    var headers = {};
    if (tokenValue) {
        headers['X-Access-Token'] = tokenValue;
    }
    if (contentType) {
        headers['Content-Type'] = contentType;
    }
    var fetchOptions = {method, headers};
    if (body) {
        fetchOptions['body'] = body;
    }
    return fetchOptions;
}

function fetchAPI(path, method, tokenValue, body, contentType, checkResponse) {
    var API_BASE = `${getApiBaseUrl()}api`;

    fetch(`${API_BASE}${path}`, getFetchOptions(method, tokenValue, body, contentType)).then(
        (response) => {
            if (response.status === 401) {
                if (tokenValue) {
                    console.error("Error 401: Unauthorized. Deleting the token.");
                    logout();

                    AuthRequired.set(true);
                }
            } else {
                checkResponse(response);
            }
        }
    );
}

async function fetchAPIAsync(path, method, tokenValue, body, contentType) {
    var API_BASE = `${getApiBaseUrl()}api`;

    return await fetch(`${API_BASE}${path}`, getFetchOptions(method, tokenValue, body, contentType));
}

export interface ILoader {
    endpoint: string;
    responseField: string;
    fromJson: (any) => IEntity;
}

export function getEntities(loader: ILoader, tokenValue, successCB: (entities: IEntity[]) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${loader.endpoint}`, 'GET', tokenValue, null, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data[loader.responseField].map(loader.fromJson));
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export async function getEntitiesAsync(loader: ILoader, tokenValue) {
    const response = await fetchAPIAsync(`/${loader.endpoint}`, 'GET', tokenValue, null, null);
    const data = await response.json();
    if (response.status === 200) {
        return data[loader.responseField].map(loader.fromJson);
    } else {
        throw Error(data.message);
    }
}

export function postEntity(endpoint, tokenValue, entity: IEntity, successCB: (key: string) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${endpoint}`, 'POST', tokenValue, entity.toJson(), "application/json",
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data.key);
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function postMedia(tokenValue, entityEndpoint, entityKey, media: AddedMedia[], successCB: () => void, errorHandler = new ErrorHandler()) {
    const data = new FormData();
    for (const [i, m] of media.entries()) {
        data.append(`file${i}`, m.file);
    }
    fetchAPI(`/${entityEndpoint}/${entityKey}/media`, "POST", tokenValue, data, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        }
    );
}

export async function postEntityAsync(endpoint, tokenValue, entity: IEntity) {
    const response = await fetchAPIAsync(`/${endpoint}`, 'POST', tokenValue, entity.toJson(), "application/json");
    const data = await response.json();
    if (response.status === 200) {
        return data.key;
    } else {
        throw Error(data.message);
    }
}

export function putEntity(tokenValue, entity: IEntity, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${entity.endpoint}/${entity.key}`, 'PUT', tokenValue, entity.toJson(), "application/json",
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

interface GetLoginSuccessResponse {
    token: string;
    user: User;
}

export function lnurlAuth(behavior: AuthBehavior, k1, initialResponseCB: (response: {k1: string, lnurl: string, qr: string}) => void, waitResponseCB: () => void, successResponseCB: (response: GetLoginSuccessResponse) => void, expiredCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${behavior}/lnurl` + (k1 ? `?k1=${k1}` : ""), 'GET', null, null, null,
        response => {
            if (response.status === 200) {
                response.json().then(
                    data => {
                        if (data.success) {
                            successResponseCB({token: data.token, user: userFromJson(data.user)});
                        } else if (data.k1) {
                            initialResponseCB({k1: data.k1, lnurl: data.lnurl, qr: data.qr});
                        } else {
                            waitResponseCB();
                        }
                    }
                );
            } else if (response.status === 410) {
                response.json().then(
                    () => {
                        expiredCB();
                    }
                );
            } else {
                errorHandler.handle(response);
            }
        });
}

export function getFeaturedAvatars(campaignKey: string, successCB: (auctionAvatars: {url: string, entity_key: string}[], listingAvatars: {url: string, entity_key: string}[]) => void) {
    fetchAPI(`/campaigns/${campaignKey}/avatars/featured`, 'GET', null, null, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data['auction_avatars'], data['listing_avatars']);
                });
            }
        }
    );
}

export function getProfile(tokenValue, nym: string, successCB: (User) => void, errorHandler = new ErrorHandler(false)) {
    fetchAPI(`/users/${nym}`, 'GET', tokenValue, null, null,
        (response) => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(userFromJson(data.user));
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export type UserProfile = {
    twitterUsername?: string,
    nostrPublicKey?: string,
    contributionPercent?: string,
    wallet?: string,
    lightningAddress?: string,
    nym?: string,
    profileImageUrl?: string,
    stallName?: string,
    stallDescription?: string,
    shippingFrom?: string,
    shippingDomesticUsd?: number,
    shippingWorldwideUsd?: number,
    nostr_private_key?: string
};

export function putProfile(tokenValue, profile: UserProfile, successCB: (user: User, publishedToNostr: boolean) => void, errorHandler = new ErrorHandler()) {
    var json: any = {};
    if (profile.twitterUsername !== undefined) {
        json.twitter_username = profile.twitterUsername;
    }
    if (profile.nostrPublicKey !== undefined) {
        json.nostr_public_key = profile.nostrPublicKey;
    }
    if (profile.contributionPercent !== undefined) {
        json.contribution_percent = profile.contributionPercent;
    }
    if (profile.wallet !== undefined) {
        json.wallet = profile.wallet;
    }
    if (profile.lightningAddress !== undefined) {
        json.lightning_address = profile.lightningAddress;
    }
    if (profile.nym !== undefined) {
        json.nym = profile.nym;
    }
    if (profile.profileImageUrl !== undefined) {
        json.profile_image_url = profile.profileImageUrl;
    }
    if (profile.stallName !== undefined) {
        json.stall_name = profile.stallName;
    }
    if (profile.stallDescription !== undefined) {
        json.stall_description = profile.stallDescription;
    }
    if (profile.shippingFrom !== undefined) {
        json.shipping_from = profile.shippingFrom;
    }
    if (profile.shippingDomesticUsd !== undefined) {
        json.shipping_domestic_usd = profile.shippingDomesticUsd;
    }
    if (profile.shippingWorldwideUsd !== undefined) {
        json.shipping_worldwide_usd = profile.shippingWorldwideUsd;
    }
    if (profile.nostr_private_key !== undefined) {
        json.nostr_private_key = profile.nostr_private_key;
    }
    fetchAPI("/users/me", 'PUT', tokenValue, JSON.stringify(json), "application/json",
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(userFromJson(data.user), data.published_to_nostr);
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putVerify(tokenValue, accountProvider: ExternalAccountProvider, resend: boolean | undefined, phrase: string | undefined, successCB: () => void, errorHandler = new ErrorHandler()) {
    let payload = {};
    if (resend) {
        payload['resend'] = true;
    } else {
        payload['phrase'] = phrase;
    }
    fetchAPI(`/users/me/verify/${accountProvider}`, 'PUT', tokenValue,
        JSON.stringify(payload), "application/json",
        response => {
            if (response.status === 200) {
                response.json().then(_ => {
                    successCB();
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putVerifyLnurl(tokenValue, k1, initialResponseCB: (response: {k1: string, lnurl: string, qr: string}) => void, waitResponseCB: () => void, successResponseCB: () => void, errorHandler = new ErrorHandler()) {
    let payload = {};
    if (k1) {
        payload['k1'] = k1;
    }
    fetchAPI("/users/me/verify/lnurl", 'PUT', tokenValue, JSON.stringify(payload), "application/json",
        response => {
            if (response.status === 200) {
                response.json().then(
                    data => {
                        if (data.success) {
                            successResponseCB();
                        } else if (data.k1) {
                            initialResponseCB({k1: data.k1, lnurl: data.lnurl, qr: data.qr});
                        } else {
                            waitResponseCB();
                        }
                    }
                );
            } else {
                errorHandler.handle(response);
            }
        });
}

export function getItem(loader: ILoader, tokenValue, key, successCB: (item) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${loader.endpoint}/${key}`, 'GET', tokenValue, null, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(loader.fromJson(data[loader.responseField])); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putPublish(tokenValue, endpoint, key, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${endpoint}/${key}/publish`, 'PUT', tokenValue, null, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        }
    );
}

export function deleteEntity(tokenValue, entity: IEntityBase, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${entity.endpoint}/${entity.key}`, 'DELETE', tokenValue, null, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
    });
}

export async function deleteEntityAsync(tokenValue, entity: IEntity) {
    const response = await fetchAPIAsync(`/${entity.endpoint}/${entity.key}`, 'DELETE', tokenValue, null, null);
    const data = await response.json();
    if (response.status === 200) {
        return true;
    } else {
        throw Error(data.message);
    }
}

export async function getAuction(key) {
    const response = await fetch(`${getApiBaseUrl()}api/auctions/${key}`)
    const auction = await response.json()
    if (response.ok) {
        return {
            itemKey: key,
            serverLoadedItem: auction.auction
        }
    }
    throw error(
        response.status,
        "Could not fetch auction on the server"
    );
}

export async function getListing(key) {
    const response = await fetch(`${getApiBaseUrl()}api/listings/${key}`)
    const listing = await response.json()
    if (response.ok) {
        return {
            itemKey: key,
            serverLoadedItem: listing.listing
        }
    }
    throw error(
        response.status,
        "Could not fetch listing on the server"
    );
}

export async function getUser(nym) {
    const response = await fetch(`${getApiBaseUrl()}api/users/${nym}`)
    const user = await response.json()
    if (response.ok) {
        return {
            stallOwnerNym: nym,
            serverLoadedUser: user.user
        }
    }
    throw error(
        response.status,
        "Could not fetch user on the server"
    );
}

export function putOrder(tokenValue, uuid: string, status: {paid?: boolean, shipped?: boolean, canceled?: boolean}, successCB: (order: Order) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/users/me/orders/${uuid}`, 'PUT', tokenValue, JSON.stringify(status), "application/json",
        response => {
            if (response.status === 200) {
                response.json().then(data => successCB(orderFromJson(data.order)));
            } else {
                errorHandler.handle(response);
            }
        });
}
