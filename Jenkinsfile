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

    def processes = [ 'get_omdb'
                    , 'get_tmdb'
                    , 'get_itunes'
                    , 'get_youtube'
                    , 'insert_movies'
                    , 'insert_movies2companies'
                    , 'insert_movies2genres'
                    , 'insert_movies2keywords'
                    , 'insert_movies2numbers'
                    , 'insert_movies2persons'
                    , 'insert_movies2posters'
                    , 'insert_movies2ratings'
                    , 'insert_movies2streams'
                    , 'insert_movies2trailers'
                    , 'insert_errored'
                    ];


    for (i = 0; i <processes.size(); i++) {

        echo "Hello"

    }

}