FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Chicago
RUN apt-get update

RUN apt-get install -y rtl-sdr git python3-pip golang

RUN pip3 install paho-mqtt

RUN go get github.com/bemasher/rtlamr

RUN cp ~/go/bin/rtlamr /usr/local/bin/rtlamr

COPY amr2mqtt.py /opt/amr2mqtt/amr2mqtt
COPY settings.py /opt/amr2mqtt/settings.py

CMD ["python3", "/opt/amr2mqtt/amr2mqtt" ]
