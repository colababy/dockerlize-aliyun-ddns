FROM python:3.6.8-alpine3.8

ENV ACCESS_KEY=ACCESS_KEY_EXAMPLE
ENV ACCESS_SECRET=ACCESS_SECRET_EXAMPLE
ENV DOMAIN=EXAMPLE.DOMAIN.COM

WORKDIR /
ADD ddns.py /ddns.py

RUN printf "%b" "*/5 * * * * python /ddns.py >> /var/log/ddns.log" > /etc/crontabs/root && \
    printf "%b" '#!'"/usr/bin/env sh\n \
if [ \"\$1\" = \"daemon\" ];  then \n \
 trap \"echo stop && killall crond && exit 0\" SIGTERM SIGINT \n \
 crond && while true; do sleep 1; done;\n \
else \n \
 exec -- \"\$@\"\n \
fi" >/entry.sh && chmod +x /entry.sh

ENTRYPOINT ["/entry.sh"]
CMD ["python", "/ddns.py"]

