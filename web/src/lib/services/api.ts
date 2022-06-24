import { goto } from "$app/navigation";
import { type Auction, fromJson as auctionFromJson, toJson } from "../types/auction";
import { type User, fromJson as userFromJson } from "../types/user";
import { isLocal, isStaging } from "../utils";
import { token, Error } from "../stores";

function setError(response) {
    response.json().then(data => { Error.set(data.message); });
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

export function getLogin(k1, cb: (data) => void) {
    fetchAPI("/login" + (k1 ? `?k1=${k1}` : ""), 'GET', null, null,
        response => {
            if (response.status === 200) {
                response.json().then(
                    data => {
                        cb(data);
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

export function postProfile(tokenValue, profile: {twitterUsername: string, contributionPercent: string}, successCB: (User) => void) {
    fetchAPI("/users/me", 'POST', tokenValue,
        JSON.stringify({twitter_username: profile.twitterUsername, contribution_percent: profile.contributionPercent}),
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(userFromJson(data.user));
                });
            } else {
                setError(response);
            }
        });
}

export function getAuctions(tokenValue, successCB: (auctions: Auction[]) => void) {
    fetchAPI("/auctions", 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => {
                    successCB(data.auctions.map(auctionFromJson));
                });
            } else {
                setError(response);
            }
        });
}

export function getAuction(tokenValue, auctionKey, successCB: (Auction) => void, errorCB: () => void = () => {}) {
    fetchAPI(`/auctions/${auctionKey}`, 'GET', tokenValue, null,
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(auctionFromJson(data.auction)); });
            } else {
                errorCB();
            }
        });
}

export function putAuction(tokenValue, auction: Auction, successCB: () => void) {
    fetchAPI(`/auctions/${auction.key}`, 'PUT', tokenValue, toJson(auction),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                setError(response);
            }
        });
}

export function postAuction(tokenValue, auction: Auction, successCB: () => void) {
    fetchAPI("/auctions", 'POST', tokenValue, toJson(auction),
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                setError(response);
            }
        });
}

export function startAuction(tokenValue, auctionKey, successCB: () => void, errorCB: () => void = () => {}) {
    fetchAPI(`/auctions/${auctionKey}/start-twitter`, 'PUT', tokenValue, null,
        response => {
            if (response.status === 200) {
                successCB();
            } else {
                setError(response);
                errorCB();
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

export function postBid(tokenValue, auctionKey, amount, successCB: (paymentRequest, paymentQr) => void) {
    fetchAPI(`/auctions/${auctionKey}/bids`, 'POST', tokenValue,
        JSON.stringify({amount}),
        response => {
            if (response.status === 200) {
                response.json().then(data => { successCB(data.payment_request, data.qr); });
            } else {
                setError(response);
            }
        });
}
