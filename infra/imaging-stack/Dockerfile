FROM php:8.2-apache

# ThaiRIS 18 free required extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql gd mbstring zip \
    && docker-php-ext-enable mysqli pdo_mysql gd mbstring zip

# Common ThaiRIS needs
RUN a2enmod rewrite headers

# Timezone / defaults
ENV TZ=UTC

WORKDIR /var/www/html
