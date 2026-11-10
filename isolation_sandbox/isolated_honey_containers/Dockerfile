# ==============================================================================
# Isolated Honey Container Dockerfile (Layer 3: Dynamic Containment Sandbox)
# Image: deception-honey-sandbox:latest
# ==============================================================================
FROM python:3.11-slim

LABEL maintainer="Principal Security Architect - Deception Architecture"
LABEL description="Air-gapped High-Interaction Honey Container with Decoy Service App"
LABEL layer="Layer-3-Isolation-Sandbox"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    SERVICE_NAME=isolation_sandbox \
    SANDBOX_CONTAINMENT_MODE=strict_internal \
    DECOY_SERVICE_PORT=8080

WORKDIR /app

# Create realistic decoy filesystem directories inside the container
RUN mkdir -p /var/www/enterprise-decoy \
             /var/backups \
             /var/log/audit \
             /home/devops/.aws \
             /home/devops/.ssh && \
    chown -R www-data:www-data /var/www/enterprise-decoy

EXPOSE 8080

USER www-data

CMD ["python", "-m", "isolation_sandbox.isolated_honey_containers.decoy_service_app"]
