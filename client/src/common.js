import dayjs from 'dayjs';
import { writable } from 'svelte/store';

export const token = writable(null);

export function fromJson(json) {
    var a = {};
    for (var k in json) {
        if (k === 'starts_at' || k === 'ends_at') {
            a[k] = dayjs(new Date(json[k])).format("YYYY-MM-DDTHH:mm");
        } else {
            a[k] = json[k];
        }
    }
    return a;
}

export function fetchAPI(path, method, token, json, checkResponse) {
    var API_BASE = "/api";
    var headers = {};
    if (token) {
        headers['X-Access-Token'] = token;
    }
    if (json) {
        headers['Content-Type'] = 'application/json';
    }
    var fetchOptions = {method, headers};
    if (json) {
        fetchOptions['body'] = json;
    }
    fetch(`${API_BASE}${path}`, fetchOptions).then(checkResponse);
}
