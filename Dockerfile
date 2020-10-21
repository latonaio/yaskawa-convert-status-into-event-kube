FROM l4t:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=yaskawa-convert-status-into-event \
    AION_HOME=/var/lib/aion 

RUN mkdir -p {AION_HOME}
WORKDIR ${AION_HOME}

# Setup Directoties
RUN mkdir -p $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/
ADD . .
RUN python3 setup.py install
CMD ["python3", "-m", "yaskawa-convert-status-into-event"]
