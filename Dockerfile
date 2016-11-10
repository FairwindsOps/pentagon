FROM python:2
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt
RUN apt-get update -qq && apt-get install -y nginx
COPY . /usr/src/app
RUN mkdocs build -d /var/www/html
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
