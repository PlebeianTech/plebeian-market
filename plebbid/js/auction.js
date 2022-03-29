var k1;

function refreshAuction(element) {
    var auction_key = element.dataset['auctionKey'];
    doGet(`/auctions/${auction_key}`,
        function(response) {
            var startsAt = new Date(response.auction.starts_at);
            element.querySelector("#starts-at").innerHTML = "Starts at: " + formatDate(startsAt) + " " + formatTime(startsAt);
            var endsAt = new Date(response.auction.ends_at);
            element.querySelector("#ends-at").innerHTML = "Ends at: " + formatDate(endsAt) + " " + formatTime(endsAt);
            var minimumBid = response.auction.minimum_bid;
            element.querySelector("#minimum-bid").innerHTML = "Minimum bid: " + minimumBid;
            var bids = response.auction.bids;
            element.querySelector("#bids").textContent = "";
            if (bids) {
                for (const b of bids) {
                    var li = document.createElement('li');
                    li.textContent = `${b.amount} (by ${b.bidder})`;
                    element.querySelector("#bids").appendChild(li);
                    if (b.payment_request) {
                        var payment = element.querySelector("#bid-payment");
                        if (b.payment_request === payment.dataset['paymentRequest']) {
                            payment.dataset['paymentRequest'] = null;
                            payment.style.display = 'none';
                            element.querySelector("#bid").style.display = 'block';
                        }
                    }
                }
            }

            setTimeout(function() { refreshAuction(element) }, 1000);
        });
}

function refreshLogin(element) {
    if (cookie('auction-jwt-token')) {
        var payment = element.querySelector("#bid-payment");
        if (!payment.dataset['paymentRequest']) {
            element.querySelector("#bid").style.display = 'block';
        }
    } else {
        element.querySelector("#bid").style.display = 'none';
        element.querySelector("#bid-payment").style.display = 'none';
        doGet("/login" + (k1 ? `?k1=${k1}` : ""),
            function(response) {
                if (response.success) {
                    cookie('auction-jwt-token', response.token, 1 * 60 * 60 * 24); // TODO: maybe just make it expire after the auction ends
                    element.querySelector("#login").innerHTML = "";
                } else if (response.k1) {
                    k1 = response.k1;
                    var doc = new DOMParser().parseFromString(response.qr, "text/xml");
                    element.querySelector("#login").appendChild(document.importNode(doc.rootElement, true));
                }
                setTimeout(function() { refreshLogin(element) }, 1000);
            });
    }
}

function bid(button) {
    var auction = document.getElementById('auction'); // TODO: get relative to button
    var auction_key = auction.dataset['auctionKey'];
    var amount = auction.querySelector("#bid-amount").value;
    doPost(`/auctions/${auction_key}/bids`, `amount=${amount}`,
        function(response) {
            var doc = new DOMParser().parseFromString(response.qr, "text/xml");
            var payment = auction.querySelector("#bid-payment");
            payment.textContent = "";
            payment.dataset['paymentRequest'] = response.payment_request;
            payment.appendChild(document.importNode(doc.rootElement, true));
            payment.style.display = 'block';
            auction.querySelector("#bid").style.display = 'none';
        });
}

function onLoadAuction(auction) {
    const elements = [
        ['starts-at', 'div', true],
        ['ends-at', 'div', true],
        ['minimum-bid', 'div', true],
        ['bids', 'ul', true],
        ['login', 'div', true],
        ['bid', 'div', false],
        ['bid-payment', 'div', false]
    ];
    for (const [elId, elType, elVisible] of elements) {
        var el = document.createElement(elType);
        el.id = elId;
        if (!elVisible) {
            el.style.display = 'none';
        }
        if (elId === 'bid') {
            var subEl = document.createElement('div');
            var input = document.createElement('input');
            input.id = 'bid-amount';
            input.type = 'number';
            subEl.appendChild(input);
            el.appendChild(subEl);

            var subEl = document.createElement('div');
            var button = document.createElement('button');
            button.onclick = function(b) { bid(b); };
            button.textContent = "Place bid";
            subEl.appendChild(button);
            el.appendChild(subEl);
        }
        auction.appendChild(el);
    }

    refreshLogin(auction);
    refreshAuction(auction);
}
