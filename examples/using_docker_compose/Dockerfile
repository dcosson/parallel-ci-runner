FROM ruby:2.3.1-alpine

RUN gem install --no-ri --no-rdoc rspec && \
    mkdir -p /app/spec

WORKDIR /app

ADD spec /app/spec
