echo "Building Docker images..."
docker build -t auth-service ./auth-service-main
docker build -t fitness-app ./business-logic-service-main


echo "Deploying stack to Docker Swarm..."
docker stack deploy -c ./docker-files-main fitness-app

