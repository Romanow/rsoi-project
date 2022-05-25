FROM openjdk:8
WORKDIR /shop-service
COPY build/libs/shop-service-1.0.0.jar .
CMD java -jar shop-service-1.0.0.jar -P:ktor.deployment.port=$PORT
