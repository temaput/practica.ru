FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/temaput/drawinvoice.git
RUN pip install git+https://github.com/temaput/tarifcalc.git
RUN pip install git+https://github.com/temaput/django-oscar-robokassa.git
ADD ./practica /code/
EXPOSE 8000
CMD gunicorn --workers=4 --bind=0.0.0.0:8000 practica.wsgi 
