# pull official base image
FROM ubuntu:20.04

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV INIT 1

RUN apt-get update 
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install git-all libclang-dev python-is-python3 python3-pip build-essential postgresql-server-dev-all nodejs npm

# Upgrade pip
RUN python -m pip install --upgrade pip

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# nodejs
WORKDIR home/frontend/
RUN npm install
RUN npm run build
WORKDIR ../../

# build project
RUN python manage.py collectstatic --noinput

# apply database
RUN python manage.py makemigrations
RUN python manage.py migrate

# add database
RUN python api/utils/add_database.py api/utils/vietnam.json
RUN python rcs/code/create_fake_data.py

# apply database
ENV INIT 0
RUN python manage.py makemigrations
RUN python manage.py migrate

# add and run as non-root user
RUN /usr/sbin/useradd -u 1000 user
USER user

EXPOSE 8000

# run gunicorn
CMD gunicorn project.wsgi:application --bind 0.0.0.0:$PORT