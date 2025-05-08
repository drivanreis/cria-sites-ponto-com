#!/bin/bash
cd ..
cd ..
docker build -t cria-sites-ponto-com .
docker-compose up -d
