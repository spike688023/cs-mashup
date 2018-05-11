FROM cs50/cli
USER root

# Set FLASK_APP
RUN echo "FLASK_APP='application.py'" >> /etc/environment

# Default port (to match CS50 IDE)
EXPOSE 8081

# Packages 
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        libcurl4-openssl-dev `# required by passenger-config` \
        libpcre3-dev `# required by passenger-config` \
        php7.1-fpm \
        php7.1-memcached \
        php7.1-mysql \
        php7.1-xdebug
RUN pip3 install Django Flask Flask-JSGlue Flask-Session raven[flask] SQLAlchemy virtualenv feedparser
ENV API_KEY=AIzaSyDJDJnf9U5ptessbyJB2RcfigzB8XWwKnE


# Install Passenger via gem, per https://www.phusionpassenger.com/library/install/standalone/install/oss/rubygems_norvm/,
# rather than apt-get, per https://www.phusionpassenger.com/library/install/standalone/install/oss/trusty/,
# else a version of nginx (compiled without ngx_http_fastcgi_module) gets installed from Passenger's repo, which yields:
# unknown directive "fastcgi_param" in nginx.conf
RUN gem install passenger -v 5.1.11

# Download any necessary files immediately, which would otherwise be downloading during the first run
RUN passenger-config install-standalone-runtime && \
    passenger-config build-native-support

# Install server's own config files
COPY ./bin/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/*
COPY ./etc/* /usr/local/etc/
RUN chmod a+r /usr/local/etc/*
RUN echo "This is CS50 Server." > /etc/motd

# When child image is built from this one, copy its files into image
COPY ./examples/flask/ /var/www/
RUN chown -R www-data:www-data /var/www
WORKDIR /var/www

# Start server within WORKDIR
CMD ["passenger", "start", "-p", "8081", "--app-type", "wsgi", "--startup-file", "passenger_wsgi.py"]
