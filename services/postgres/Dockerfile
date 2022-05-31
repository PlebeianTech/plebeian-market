FROM postgres:14-bullseye

# TODO: ideally we don't hardcode these here,
# but for now this works fine as these values are only used when creating a new database,
# which only happens for dev & test (which have the same values hardcoded)
# for production, the values are read from "/secrets/db.json"
ENV POSTGRES_DB market
ENV POSTGRES_USER pleb
ENV POSTGRES_PASSWORD plebpass
