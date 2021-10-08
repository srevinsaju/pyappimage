FROM python:3.9-buster

RUN mkdir /src
WORKDIR /src

COPY . .
RUN pip3 install .
RUN rm -rf /src
CMD python3 -m pyappimage.build
