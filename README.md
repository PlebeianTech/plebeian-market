# plebeian.market auctions

```./test.sh``` (to run the automated tests)

```./dev.sh``` (to start the development environment)

```./prod.sh``` (to (re)start the production environment)

## Testing from the command line

* adding a seller with key "1234": `curl -i -X POST -d "key=1234" https://plebeian.market/sellers`
* listing auctions for this seller: `curl -i -X GET https://plebeian.market/sellers/1234/auctions`
* adding an auction for this seller: `curl -i -X POST -d "starts_at=2022-03-30T12:00&ends_at=2022-03-31T13:00&minimum_bid=10" https://plebeian.market/sellers/1234/auctions`
* deleting the auction: `curl -i -X DELETE https://plebeian.market/sellers/1234/auctions/1`
