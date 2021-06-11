This is DBTask Python Microservice

It contains a dockerfile which is used to create a docker image that is used in

containerDefinition part of ECS TaskDefinition for dbtask ECS service task

This microservice is hosted on a ECS Container EC2 Instance in a ECS cluster inside a private subnet and behind

a Private Application Load Balancer

This is the Backend Microservice and therefore is placed in a private subnet

Only the frontend facing microservices communicate with this service via private ALB
