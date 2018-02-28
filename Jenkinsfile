#!groovy

node {
    registry_url = "${env.REGISTRY_URL}"
    build_tag = "latest"
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
                    ]];
    stage 'Git'
    git([ url: 'https://github.com/kinoreel/kino-gather.git', branch: 'master'])

    for (i = 0; i <processes.size(); i++) {

        maintainer_name = "${env.MAINTAINER}"
        container_name = "gather-${apis[i]}"
        image_name = "${registry_url}/${maintainer_name}/${container_name}:${build_tag}"
        stage "Building ${image_name} Docker image"
        container = docker.build("${image_name}", "--build-arg PROCESS = ${processes[i]} \
                                                   --build-arg KAFKA_BROKER = ${env.KAFKA_BROKER} \
                                                   --build-arg OMDB_API_KEY = ${env.OMDB_API_KEY} \
                                                   --build-arg TMDB_API_KEY = ${env.TMDB_API_KEY} \
                                                   --build-arg YOUTUBE_API_KEY = ${env.YOUTUBE_API_KEY} \
                                                   --build-arg DB_SERVER = ${env.DB_SERVER} \
                                                   --build-arg DB_PORT = ${env.DB_PORT} \
                                                   --build-arg DB_DATABASE = ${env.DB_DATABASE} \
                                                   --build-arg DB_USER = ${env.DB_USER} \
                                                   --build-arg DB_PASSWORD = ${env.DB_PASSWORD}")

        stage "Pushing ${image_name} Docker image"

        sh "docker rmi ${image_name}"

        currentBuild.result = 'SUCCESS'
    }
}