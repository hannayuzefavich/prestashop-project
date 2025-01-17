FROM prestashop/prestashop:1.7.8

COPY ./apache/ssl.conf /etc/apache2/sites-available/ssl.conf

COPY ./certs/localhost.crt /etc/ssl/certs/localhost.crt
COPY ./certs/localhost.key /etc/ssl/private/localhost.key

RUN rm -rf /var/www/html/*
COPY ./prestadata /var/www/html

RUN chmod -R 777 /var/www/html

RUN update-ca-certificates && a2enmod ssl && a2ensite ssl && a2enmod rewrite
