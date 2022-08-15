import { goto } from "$app/navigation";
import { token, Error } from "$lib/stores";
import type { IEntity } from "$lib/types/base";
import { type UserNotification, fromJson as userNotificationFromJson, PostUserNotification } from "$lib/types/notification";
import { type User, fromJson as userFromJson } from "$lib/types/user";
import { isLocal, isStaging } from "$lib/utils";

export class ErrorHandler {
    setError: boolean;
    onError: () => void;

    public constructor(setError: boolean = true, onError: () => void = () => {}) {
        this.setError = setError;
        this.onError = onError;
    }

    public handle(response) {
        if (this.setError) {
            response.json().then(data => { Error.set(data.message); });
        }

        this.onError();
    }
}

function fetchAPI(path, method, tokenValue, json, checkResponse) {
    var API_BASE;
    if (isLocal()) {
        API_BASE = "http://localhost:5000/api";
    } else if (isStaging()) {
        API_BASE = "https://staging.plebeian.market/api";
    } else {
        API_BASE = "https://plebeian.market/api";
    }

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
    fetch(`${API_BASE}${path}`, fetchOptions).then(
        (response) => {
            if (response.status === 401) {
                if (tokenValue) {
                    console.log("Error 401: Unauthorized. Deleting the token.");
                    token.set(null);
                    localStorage.removeItem('token');
                    goto("/login");
                }
            } else {
                checkResponse(response);
            }
        }
    );
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

export function postEntity(tokenValue, entity: IEntity, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${entity.endpoint}`, 'POST', tokenValue, entity.toJson(),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
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

export interface GetLoginInitialResponse {
    k1: string;
    lnurl: string;
    qr: string;
}

export interface GetLoginSuccessResponse {
    token: string;
    user: User;
}

export function getLogin(k1, initialResponseCB: (response: GetLoginInitialResponse) => void, waitResponseCB: () => void, successResponseCB: (response: GetLoginSuccessResponse) => void) {
    fetchAPI("/login" + (k1 ? `?k1=${k1}` : ""), 'GET', null, null,
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
            }
        });
}

export function getFeatured(loader: ILoader, successCB: (items: any[]) => void) {
    fetchAPI(`/${loader.endpoint}/featured`, 'GET', null, null,
            response => {
                if (response.status === 200) {
                    response.json().then(data => {
                        successCB(data[loader.responseField].map(loader.fromJson));
                    });
                }
            });
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

export function putProfile(tokenValue, profile: {twitterUsername?: string, contributionPercent?: string, xpub?: string}, successCB: (user: User) => void, errorHandler = new ErrorHandler()) {
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

export function putVerifyTwitter(tokenValue, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/users/me/verify-twitter", 'PUT', tokenValue,
        JSON.stringify({}),
        response => {
            if (response.status === 200) {
                response.json().then(data => {
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

export function putStart(tokenValue, endpoint, auctionKey, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/${endpoint}/${auctionKey}/start-twitter`, 'PUT', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        }
    );
}

export function deleteEntity(tokenValue, entity: IEntity, successCB: () => void) {
    fetchAPI(`/${entity.endpoint}/${entity.key}`, 'DELETE', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            }
    });
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

export function postBid(tokenValue, auctionKey, amount, successCB: (paymentRequest, paymentQr, messages: string[]) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/bids`, 'POST', tokenValue,
        JSON.stringify({amount}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.payment_request, data.qr, data.messages); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putBuy(tokenValue, listingKey, successCB: (contributionAmount, contributionPaymentRequest, contributionPaymentQr, amount, address, addressQr, messages: string[]) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/listings/${listingKey}/buy`, 'PUT', tokenValue,
        JSON.stringify({}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.contribution_amount, data.contribution_payment_request, data.contribution_payment_qr, data.amount, data.address, data.address_qr, data.messages); });
            } else {
                errorHandler.handle(response);
            }
        });
}
