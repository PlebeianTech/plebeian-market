# plebeian auctions

## Running locally

```python3 -m venv venv```

```source venv/bin/activate```

```pip install -r requirements.txt```

```export FLASK_APP=plebbid.main```

```flask run```

## Running with docker-compose

```cp docker-compose.dev.yml docker-compose.override.yml``` (for development mode)

```docker-compose build```

```docker-compose up```

## Testing from the command line

* adding a seller with key "1234": `curl -i -X POST -d "key=1234" http://plebbid.21art.gallery/sellers`
* listing auctions for this seller: `curl -i -X GET http://plebbid.21art.gallery/sellers/1234/auctions`
* adding an auction for this seller: `curl -i -X POST -d "starts_at=2022-03-30T12:00&ends_at=2022-03-31T13:00&minimum_bid=10" http://plebbid.21art.gallery/sellers/1234/auctions`
* deleting the auction: `curl -i -X DELETE http://plebbid.21art.gallery/sellers/1234/auctions/1`
