import { goto } from "$app/navigation";
import { token } from "./stores";

export function fetchAPI(path, method, tokenValue, json, checkResponse) {
    var isLocal = window.location.href.indexOf("localhost") != -1 || window.location.href.indexOf("127.0.0.1") != -1 || window.location.href.indexOf("0.0.0.0") != -1;
    var API_BASE = (isLocal) ? "http://localhost:5000/api" : "https://plebeian.market/api";
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
                    goto("/login");
                }
            } else {
                checkResponse(response);
            }
        }
    );
}
