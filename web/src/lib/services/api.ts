import { goto } from "$app/navigation";
import { type Auction, fromJson as auctionFromJson } from "../types/auction";
import { type User, fromJson as userFromJson } from "../types/user";
import { isLocal, isStaging } from "../utils";
import { token, Error } from "../stores";

let currentTime = new Date();

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

export function getFeaturedAuctions(successCB: (auctions: Auction[]) => void) {
    fetchAPI("/auctions/featured", 'GET', null, null,
            response => {
                if (response.status === 200) {
                    response.json().then(data => {
                        successCB(data.auctions.map(auctionFromJson));
                    });
                }
            });
}

export function getProfile(tokenValue, successCB: (User) => void) {
    fetchAPI("/users/me", 'GET', tokenValue, null,
        (response) => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(userFromJson(data.user));
                });
            }
        });
}

export function postProfile(tokenValue, profile: {twitterUsername: string, contributionPercent: string}, successCB: (User) => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/users/me", 'POST', tokenValue,
        JSON.stringify({twitter_username: profile.twitterUsername, contribution_percent: profile.contributionPercent}),
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

export function getAuctions(tokenValue, successCB: (auctions: Auction[]) => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/auctions", 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data.auctions.map(auctionFromJson));
                });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function getAuction(tokenValue, auctionKey, successCB: (Auction) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}`, 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(auctionFromJson(data.auction)); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putAuction(tokenValue, auction: Auction, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auction.key}`, 'PUT', tokenValue, auction.toJson(),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

export function postAuction(tokenValue, auction: Auction, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI("/auctions", 'POST', tokenValue, auction.toJson(),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

export function startAuction(tokenValue, auctionKey, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/start-twitter`, 'PUT', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        }
    );
}

export function deleteAuction(tokenValue, auctionKey, successCB: () => void) {
    fetchAPI(`/auctions/${auctionKey}`, 'DELETE', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            }
    });
}

export function unfeatureAuction(tokenValue, auctionKey, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}`, 'PUT', tokenValue,
        JSON.stringify({"is_featured": false}),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}

export function postBid(tokenValue, auctionKey, amount, successCB: (paymentRequest, paymentQr) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/bids`, 'POST', tokenValue,
        JSON.stringify({amount}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.payment_request, data.qr); });
            } else {
                errorHandler.handle(response);
            }
        });
}

export function putBuy(tokenValue, auctionKey, successCB: (paymentRequest, paymentQr) => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/buy`, 'PUT', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.payment_request, data.qr); });
            } else {
                errorHandler.handle(response);
            }
        });
}


export function setLock(tokenValue, auctionKey, successCB: () => void, errorHandler = new ErrorHandler()) {
    fetchAPI(`/auctions/${auctionKey}/set_lock`, 'PUT', tokenValue, {lock_expiry: new Date(currentTime.setMinutes(currentTime.getMinutes()+3))},
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                errorHandler.handle(response);
            }
        });
}