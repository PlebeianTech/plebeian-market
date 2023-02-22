import { Error as ErrorStore } from "$lib/stores";
import type { IEntity } from "$lib/types/base";
import { type Sale, fromJson as saleFromJson } from "$lib/types/sale";
import { type UserNotification, fromJson as userNotificationFromJson, PostUserNotification } from "$lib/types/notification";
import { type User, UserResume, fromJson as userFromJson } from "$lib/types/user";
import { getApiBaseUrl, logout, requestLoginModal } from "$lib/utils";
import { error } from '@sveltejs/kit';

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

function getFetchOptions(method, tokenValue, json) {
    var headers = {};
    if (tokenValue) {
        headers['X-Access-Token'] = tokenValue;
    }
    if (json) {
        headers['Content-Type'] = 'application/json';
    }
    var fetchOptions = {method, headers};
    if (json) {
        fetchOptions['body'] = json;
    }
    return fetchOptions;
}

function fetchAPI(path, method, tokenValue, json, checkResponse) {
    var API_BASE = `${getApiBaseUrl()}api`;

    fetch(`${API_BASE}${path}`, getFetchOptions(method, tokenValue, json)).then(
        (response) => {
            if (response.status === 401) {
                if (tokenValue) {
                    console.log("Error 401: Unauthorized. Deleting the token.");
                    logout();

                    requestLoginModal();
                }
            } else {
                checkResponse(response);
            }
        }
    );
}

async function fetchAPIAsync(path, method, tokenValue, json) {
    var API_BASE = `${getApiBaseUrl()}api`;

    return await fetch(`${API_BASE}${path}`, getFetchOptions(method, tokenValue, json));
}

export interface ILoader {
    endpoint: string;
    responseField: string;
    fromJson: (any) => IEntity;
}

export function getEntities(loader: ILoader, tokenValue, successCB: (entities: IEntity[]) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${loader.endpoint}`, 'GET', tokenValue, null,
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
    const response = await fetchAPIAsync(`/${loader.endpoint}`, 'GET', tokenValue, null);
    const data = await response.json();
    if (response.status === 200) {
        return data[loader.responseField].map(loader.fromJson);
    } else {
        throw Error(data.message);
    }
}

export function postEntity(endpoint, tokenValue, entity: IEntity, successCB: (key: string) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${endpoint}`, 'POST', tokenValue, entity.toJson(),
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

export async function postEntityAsync(endpoint, tokenValue, entity: IEntity) {
    const response = await fetchAPIAsync(`/${endpoint}`, 'POST', tokenValue, entity.toJson());
    const data = await response.json();
    if (response.status === 200) {
        return data.key;
    } else {
        throw Error(data.message);
    }
}

export function putEntity(tokenValue, entity: IEntity, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${entity.endpoint}/${entity.key}`, 'PUT', tokenValue, entity.toJson(),
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

export function loginLnurl(k1, initialResponseCB: (response: {k1: string, lnurl: string, qr: string}) => void, waitResponseCB: () => void, successResponseCB: (response: GetLoginSuccessResponse) => void, expiredCB: () => void) {
    fetchAPI("/login/lnurl" + (k1 ? `?k1=${k1}` : ""), 'GET', null, null,
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
            }
        });
}

export function loginNostr(npub: string, verificationPhrase: string | null, initialResponseCB: () => void = () => {}, successResponseCB: (response: GetLoginSuccessResponse) => void = (_) => {}, invalidVerificationPhraseCB: () => void = () => {}) {
    let params: any = {npub};
    if (verificationPhrase !== null) {
        params.verification_phrase = verificationPhrase;
    }
    fetchAPI("/login/nostr", 'PUT', null, JSON.stringify(params),
        response => {
            if (response.status === 200) {
                response.json().then(
                    data => {
                        if (data.success) {
                            successResponseCB({token: data.token, user: userFromJson(data.user)});
                        } else {
                            initialResponseCB();
                        }
                    }
                );
            } else if (response.status === 400) {
                response.json().then(
                    data => {
                        if (data.invalid_verification_phrase) {
                            invalidVerificationPhraseCB();
                        }
                    }
                );
            }
        }
    );
}

export function getFeaturedAvatars(campaignKey: string, successCB: (auctionAvatars: {url: string, entity_key: string}[], listingAvatars: {url: string, entity_key: string}[]) => void) {
    fetchAPI(`/campaigns/${campaignKey}/avatars/featured`, 'GET', null, null,
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
    fetchAPI(`/users/${nym}`, 'GET', tokenValue, null,
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

export function putProfile(tokenValue, profile: {twitterUsername?: string, contributionPercent?: string, xpub?: string, nym?: string, stallName?: string, stallDescription?: string, nostr_private_key?: string}, successCB: (user: User) => void, errorHandler = new ErrorHandler()) {
    var json: any = {};
    if (profile.twitterUsername !== undefined) {
        json.twitter_username = profile.twitterUsername;
    }
    if (profile.contributionPercent !== undefined) {
        json.contribution_percent = profile.contributionPercent;
    }
    if (profile.xpub !== undefined) {
        json.xpub = profile.xpub;
    }
    if (profile.nym !== undefined) {
        json.nym = profile.nym;
    }
    if (profile.stallName !== undefined) {
        json.stall_name = profile.stallName;
    }
    if (profile.stallDescription !== undefined) {
        json.stall_description = profile.stallDescription;
    }
    if (profile.nostr_private_key !== undefined) {
        json.nostr_private_key = profile.nostr_private_key;
    }
    fetchAPI("/users/me", 'PUT', tokenValue, JSON.stringify(json),
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(userFromJson(data.user));
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function getResume(tokenValue, successCB: (resume: UserResume) => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/users/me/resume", 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(UserResume.fromJson(data));
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putResume(tokenValue, resume: UserResume, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/users/me/resume", 'PUT', tokenValue, JSON.stringify(resume.toJson()),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

export function getUserNotifications(tokenValue, successCB: (notifications: UserNotification[]) => void) {
    fetchAPI("/users/me/notifications", 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data.notifications.map(userNotificationFromJson));
                });
            }
        })
}

export function putUserNotifications(tokenValue, notifications: PostUserNotification[], successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/users/me/notifications", 'PUT', tokenValue,
        JSON.stringify({'notifications': notifications.map(n => n.toJson())}),
        response => {
            if (response.status === 200) {
                response.json().then(successCB);
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putVerifyTwitter(tokenValue, resend: boolean | undefined, phrase: string | undefined, successCB: () => void, errorHandler = new ErrorHandler()) {
    let payload = {};
    if (resend) {
        payload['resend'] = true;
    } else {
        payload['phrase'] = phrase;
    }
    fetchAPI("/users/me/verify/twitter", 'PUT', tokenValue,
        JSON.stringify(payload),
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

export function getItem(loader: ILoader, tokenValue, key, successCB: (item) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${loader.endpoint}/${key}`, 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(loader.fromJson(data[loader.responseField])); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putAuctionFollow(tokenValue, auctionKey: string, follow: boolean, successCB: (message: string) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/follow`, 'PUT', tokenValue, JSON.stringify({follow}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.message); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function publish(tokenValue, endpoint, key, useTwitter: boolean, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${endpoint}/${key}/publish`, 'PUT', tokenValue, JSON.stringify({twitter: useTwitter}),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        }
    );
}

export function deleteEntity(tokenValue, entity: IEntity, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${entity.endpoint}/${entity.key}`, 'DELETE', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
    });
}

export async function deleteEntityAsync(tokenValue, entity: IEntity) {
    const response = await fetchAPIAsync(`/${entity.endpoint}/${entity.key}`, 'DELETE', tokenValue, null);
    const data = await response.json();
    if (response.status === 200) {
        return true;
    } else {
        throw Error(data.message);
    }
}

export function hideAuction(tokenValue, auctionKey, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}`, 'PUT', tokenValue,
        JSON.stringify({"is_hidden": true}),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

export function postBid(tokenValue, auctionKey, amount, skip_invoice, successCB: (paymentRequest, paymentQr, messages: string[]) => void, badgeRequiredCB: (badge: number) => void = (_) => {}, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/bids`, 'POST', tokenValue,
        JSON.stringify({amount, skip_invoice}),
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data.payment_request, data.qr, data.messages);
                });
            } else if (response.status === 402) {
                response.json().then(data => {
                    badgeRequiredCB(data.required_badge);
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function buyBadge(tokenValue, badge, campaignKey, successCB: (sale: Sale) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/badges/${badge}/buy`, 'PUT', tokenValue,
        JSON.stringify({campaign_key: campaignKey}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(saleFromJson(data.sale)); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function buyListing(tokenValue, listingKey, successCB: (sale: Sale) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/listings/${listingKey}/buy`, 'PUT', tokenValue,
        JSON.stringify({}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(saleFromJson(data.sale)); });
            } else {
                errorHandler.handle(response);
            }
        });
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

export async function getCampaign(key) {
    if (!key) {
        return {
            campaignKey: null,
            serverLoadedCampaign: null
        }
    }

    const response = await fetch(`${getApiBaseUrl()}api/campaigns/${key}`)
    const campaign = await response.json()
    if (response.ok) {
        return {
            campaignKey: key,
            serverLoadedCampaign: campaign.campaign
        }
    }
    throw error(
        response.status,
        "Could not fetch campaign on the server"
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
