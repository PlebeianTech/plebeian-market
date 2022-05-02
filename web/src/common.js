import dayjs from 'dayjs';

import { token } from "./stores.js";

export function fromJson(json) {
    var a = {};
    for (var k in json) {
        if (k === 'start_date') {
            a.start_date = json[k] ? dayjs(new Date(json[k])).format("YYYY-MM-DDTHH:mm") : null;
            a.started = a.start_date && dayjs(a.start_date).isBefore(dayjs());
        } else if (k === 'end_date') {
            a.end_date = json[k] ? dayjs(new Date(json[k])).format("YYYY-MM-DDTHH:mm") : null;
            a.ended = a.end_date && dayjs(a.end_date).isBefore(dayjs());
        } else if (k === 'duration_hours') {
            a.duration_hours = json[k];
            let days = 0, hours = a.duration_hours;
            if (hours >= 24) {
                days = Math.floor(hours / 24);
                hours = hours % 24;
            }
            let durations = [];
            if (days > 0) {
                durations.push(`${days} day${ days > 1 ? "s" : ""}`);
            }
            if (hours > 0) {
                durations.push(`${hours} hour${ hours > 1 ? "s" : ""}`);
            }
            a.duration_str = durations.join(" and ");
        } else {
            a[k] = json[k];
        }
    }
    return a;
}

export function fetchAPI(path, method, tokenValue, json, checkResponse) {
    var isLocal = window.location.href.indexOf("localhost") != -1 || window.location.href.indexOf("127.0.0.1") != -1 || window.location.href.indexOf("0.0.0.0") != -1;
    var API_BASE = (isLocal) ? "/api" : "https://plebeian.market/api";
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
                console.log("Error 401: Unauthorized. Deleting the token.");
                token.set(null);
            } else {
                checkResponse(response);
            }
        }
    );
}
