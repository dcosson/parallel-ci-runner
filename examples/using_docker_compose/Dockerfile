FROM alpine:3.4

RUN apk --no-cache add bash ruby ruby-dev && \
    gem install --no-ri --no-rdoc rspec && \
    mkdir -p /app/spec

WORKDIR /app

ADD spec /app/spec
