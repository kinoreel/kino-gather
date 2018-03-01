#!groovy


node {

    stage 'Git'

    echo "${env.BRANCH_NAME}"

    git([ url: 'https://github.com/kinoreel/kino-gather.git', branch: "${env.BRANCH_NAME}"])


    stage 'Creating Docker image'

    registry_url = "https://index.docker.io/v1/"
    docker_creds_id = "1"

    docker.withRegistry("${registry_url}", "${docker_creds_id}") {

        maintainer_name = "kinoreel"
        container_name = "gather"
        build_tag = "latest"

        stage "Building Docker image"

        image = "${maintainer_name}/${container_name}:${build_tag}"
        container = docker.build("${image}")

        if ("${env.BRANCH_NAME}" == "${env.BRANCH_NAME}")
        {
            stage "Pushing Docker image"
            container.push()
        }

    }

    stage 'Cleaning Docker image'

    sh 'docker rmi kinoreel/gather --force'


    stage 'Pushing to kubernetes'

    def processes = [ 'omdb'
                    , 'tmdb'
                    , 'trailer'
                    , 'itunes'
                    , 'youtube'
                    , 'movies'
                    , 'movies2companies'
                    , 'movies2genres'
                    , 'movies2keywords'
                    , 'movies2numbers'
                    , 'movies2persons'
                    , 'movies2ratings'
                    , 'movies2streams'
                    , 'movies2trailers'
                    , 'errored'];

    for (i = 0; i <processes.size(); i++) {

        sh "kubectl apply -f kubernetes-deployments/${processes[i]}-deployment.yaml"

    }

}