function buildXhr(successCB, errorCB) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var resp = JSON.parse(xhr.responseText);
                successCB(resp);
            } else if (errorCB) {
                errorCB(resp, xhr.status);
            }
        }
    }
    return xhr;
}

function doPost(path, data, successCB, errorCB) {
    var xhr = buildXhr(successCB, errorCB);
    xhr.open('POST', `${API_URL}${path}`);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var token = sessionStorage.getItem('token');
    if (token) {
        xhr.setRequestHeader("X-Access-Token", token);
    }
    xhr.send(data);
    return false;
}

function doGet(path, successCB, errorCB) {
    var xhr = buildXhr(successCB, errorCB);
    xhr.open('GET', `${API_URL}${path}`, true);
    var token = sessionStorage.getItem('token');
    if (token) {
        xhr.setRequestHeader("X-Access-Token", token);
    }
    xhr.send(null);
    return false;
}

function formatDate(d) {
    return d.toLocaleString('default', { day: 'numeric' }) + " " + d.toLocaleString('default', { month: 'short' }) + " " + d.toLocaleString('default', { year: 'numeric' });
}

function formatTime(d) {
    return d.toLocaleString('default', { hour12: false, hour: 'numeric', minute: 'numeric' });
}
