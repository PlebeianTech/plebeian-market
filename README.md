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
