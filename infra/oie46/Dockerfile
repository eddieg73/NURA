FROM eclipse-temurin:17-jre

# OIE 4.6.0 GA — NuraTech containerized distribution (per NURATECH build directive)
COPY oie /opt/oie
WORKDIR /opt/oie

# Env-merge entrypoint (same config keys verified in 4.6.0 conf/mirth.properties)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080 8443 6661
ENTRYPOINT ["/entrypoint.sh"]
CMD ["./oieserver"]
