FROM monolithos/setzer

WORKDIR /app
COPY . .
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/docker-entrypoint.sh"]