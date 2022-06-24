# plebeian.market auctions

### Quickstart:

```./scripts/test.sh``` to run the automated tests for the API

```./scripts/dev.sh``` to start the development environment: database, API and "settle bids" service
```cd web && npm run dev``` to run the web app

```./scripts/prod.sh``` to (re)start the production environment

### Setup instructions for debian-based systems:


- Install curl:

    - ```sudo apt-get install curl```

- Install docker:

    - ```curl -fsSL https://get.docker.com -o get-docker.sh```
    - ```sudo sh get-docker.sh```

By default, the docker command can only be run the root user or by a user in the docker group. For production environments, you will want to use a dedicated user account such as `www`:

- Create user account and add to sudo and docker groups:
    - ```adduser www```
    - ```usermod -aG sudo www```
    - ```usermod -aG docker ${USER}```

- Confirm that your user is now added to the sudo and docker groups:
    - ```su - ${USER}```
    - ```groups```
adduser www && usermod -aG sudo www
```
Output
www sudo docker
```

- Install docker-compose:

  - ```sudo curl -L https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose```
  - ```sudo chmod +x /usr/local/bin/docker-compose```

- Install git and clone the repository:
  - ```sudo apt-get install git```
  - ```git clone https://github.com/PlebeianTech/plebeian-market.git```

- Install nodejs and npm:
  - ```sudo apt-get install software-properties-common```
  - ```curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -```
  - ```sudo apt-get install nodejs```

- Restart docker:
  - ```sudo systemctl restart docker```

- Run the api tests:  
  - ```cd plebeian-market```
  - ```./scripts/test.sh```

Test output should look similar to this if the tests were successful:

  ```
  plebeian-market-test-1         | Ran 1 test in 11.379s
  plebeian-market-test-1         | 
  plebeian-market-test-1         | OK
  ```

### To start development environment:
- Start the API:
  - ```cd plebeian-market```
  - ```./scripts/dev.sh``` and leave it running.
- In a new terminal, install the components with npm:
  - ```cd plebeian-market/web```
  - ```npm install```
- And start the webapp:
  - ```npm run dev```
- Heed the warning:
  - ```Note that all files in the following directories will be accessible to anyone on your network: src/lib, src/routes, .svelte-kit, src, node_modules```
- The ip address where the webapp is served will show in your console (likely a `192.x.x.x:3000`, `172.x.x.x:3000`, or `10.x.x.x:3000`). Open that address in your web browser to see the webapp.

For development, logging in via lightning can be cumbersome since your lightning wallet may have difficulty communicating with a page being served only on your local network. Alternatively, you can 
### Simulate a login:

- Find your postgres container ID :
  - ```docker ps```
  - Output from ```docker ps``` will resemble this:
```
CONTAINER ID   IMAGE                COMMAND                  CREATED       STATUS                 PORTS                                       NAMES
b56774c2e986   plebeianmarket-api   "flask settle-bids"      8 hours ago   Up 2 hours                                                         plebeian-market-settle-bids-1
d357d05a9fa2   plebeianmarket-api   "bash -c 'flask db u…"   8 hours ago   Up 2 hours (healthy)   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   plebeian-market-api-1
3518d3710c1e   plebeian-market_db   "docker-entrypoint.s…"   6 days ago    Up 2 hours             5432/tcp                                    plebeian-market-db-1
```
  - Copy the container ID that corresponds with ```plebeian-market_db```
  - Open a bash shell inside the container:
    - ```docker exec it <container ID> bash```
  - You will now be at a bash prompt resembling ```root@3518d3710c1e:/#```
  - Connect to the `market` database as user `pleb` using `psql`:
    - ```psql -U pleb market```
  - Look around with `\dt` and your output should resemble this:
```
market=# \dt
            List of relations
 Schema |      Name       | Type  | Owner 
--------+-----------------+-------+-------
 public | alembic_version | table | pleb
 public | auctions        | table | pleb
 public | bids            | table | pleb
 public | lnauth          | table | pleb
 public | media           | table | pleb
 public | state           | table | pleb
 public | users           | table | pleb
(7 rows)
```
  - Set a key to the pending authorization requests:
    - ```market=# update lnauth set key = 123;```

This will simulate a lightning wallet logging in successfully. From here, you can try out creating an auction and bidding on auctions.

This project was built with <a href="https://flask.palletsprojects.com">Flask</a> for the API and <a href="https://svelte.dev/">Svelte</a> for the webapp. The styling is done using <a href="https://tailwindcss.com/">Tailwind</a>.
