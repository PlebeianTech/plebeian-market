function buildXhr(successCB, errorCB) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var resp = JSON.parse(xhr.responseText);
                successCB(resp);
            } else if (errorCB) {
                errorCB(resp);
            }
        }
    }
    return xhr;
}

function doPost(path, data, successCB, errorCB) {
    var xhr = buildXhr(successCB, errorCB);
    xhr.open('POST', `${BASE_URL}${path}`);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var token = cookie('auction-jwt-token');
    if (token) {
        xhr.setRequestHeader("X-Access-Token", token);
    }
    xhr.send(`${data}`);
    return false;
}

function doGet(path, successCB, errorCB) {
    var xhr = buildXhr(successCB, errorCB);
    xhr.open('GET', `${BASE_URL}${path}`, true);
    var token = cookie('auction-jwt-token');
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

function cookie(name, value, seconds) {
    if(arguments.length < 2) { // read cookie
        var cookies = document.cookie.split(";")
        for(var i=0; i < cookies.length; i++) {
            var c = cookies[i].replace(/^\s+/, "");
            if(c.indexOf(name + "=") == 0) {
                return decodeURIComponent(c.substring(name.length + 1).split("+").join(" "));
            }
        }
        return null;
    }

    // write cookie
    var expiry = null;
    if (seconds) {
        var date = new Date();
        date.setTime(date.getTime() + seconds * 1000);
        expiry = date.toGMTString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + (seconds ? ";expires=" + expiry : "") + ";path=/";
}
