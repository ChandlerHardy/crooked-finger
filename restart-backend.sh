#!/bin/bash
# Usage: ./restart-backend.sh <OCI_IP_ADDRESS>
OCI_IP="${1:?Usage: $0 <OCI_IP_ADDRESS>}"
ssh ubuntu@"$OCI_IP" << 'ENDSSH'
cd /home/ubuntu/crooked-finger
docker compose -f docker-compose.backend.yml restart backend
docker compose -f docker-compose.backend.yml logs --tail=20 backend
ENDSSH
