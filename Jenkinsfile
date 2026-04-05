pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t airquality-app .'
            }
        }

        stage('Run Pipeline') {
            steps {
                sh 'docker run --rm airquality-app'
            }
        }
    }
}
