echo "Building Docker images..."
docker pull sebastianbadea0/auth-service:latest
docker pull sebastianbadea0/db-service:latest
docker pull sebastianbadea0/fitness-app:latest

docker config rm kong_config
docker config create kong_config ./api-gateway-kong-main/kong.yml


echo "Deploying stack to Docker Swarm..."
docker stack deploy -c ./docker-files-main/docker-compose.yml fitnessapp

docker service update --image sebastianbadea0/auth-service:latest auth-service
docker service update --image sebastianbadea0/db-service:latest db-service
docker service update --image sebastianbadea0/fitness-app:latest fitness-app