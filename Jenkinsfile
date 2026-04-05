pipeline {
    agent any

    environment {
        AZURE_CONN_STR = credentials('azure-conn-str')
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t airquality-app .'
            }
        }

        stage('Run Pipeline') {
            steps {
                sh 'docker run --rm -e AZURE_CONN_STR="$AZURE_CONN_STR" airquality-app'
            }
        }
    }
}
