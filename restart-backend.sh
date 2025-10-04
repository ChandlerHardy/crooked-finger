#!/bin/bash
ssh ubuntu@150.136.38.166 << 'ENDSSH'
cd /home/ubuntu/crooked-finger
docker compose -f docker-compose.backend.yml restart backend
docker compose -f docker-compose.backend.yml logs --tail=20 backend
ENDSSH
