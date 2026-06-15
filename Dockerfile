FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --upgrade pip 
RUN pip3 install -r requirements.txt 

COPY ./core /app

RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn","core.wsgi:application","--bind","0.0.0.0:8000","--workers","3"]