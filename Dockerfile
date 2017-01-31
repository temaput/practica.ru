FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/temaput/drawinvoice.git
RUN pip install git+https://github.com/temaput/tarifcalc.git
ADD ./practica /code/
