#!groovy

node {
    registry_url = "localhost:5000"
    docker_creds_id = "1"
    build_tag = "latest"

    stage 'Git'
    git([ url: 'https://github.com/kinoreel/kino-gather.git', branch: ${BRANCH}])

    docker.withRegistry("${registry_url}") {
        maintainer_name = "kino"
        container_name = "gather"
        stage "Building Docker image"
        echo "Building the docker image"
        container = docker.build("${maintainer_name}/${container_name}:${build_tag}", ' --build-arg KAFKA_BROKER=${KAFKA_BROKER} --build-arg API_KEY=${API_KEY} --build-arg API_NAME=${API_NAME} .')

        stage 'Testing docker'
        container.inside {
          sh 'sh test.sh'
        }

        stage "Pushing Docker image"
        container.push()

        currentBuild.result = 'SUCCESS'
    }
}