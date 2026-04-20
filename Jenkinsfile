
pipeline {

    agent any

    stages {

        stage('Checkout') {

            steps {

                echo 'Recuperation du code...'

                checkout scm

            }

        }

        stage('Build Docker Image') {

            steps {

                sh 'docker build -t flask-app .'

            }

        }

        stage('Deploy') {

            steps {

                sh 'docker stop flask-app || true'

                sh 'docker rm flask-app || true'

                sh 'docker run -d --name flask-app -p 5000:5000 flask-app'

            }

        }

        stage('Verify') {

            steps {

                sh 'sleep 5'

                sh 'curl -f http://192.168.56.10:5000/health'

            }

        }

    }

    post {

        success { echo 'Deploiement reussi !' }

        failure { echo 'Echec du pipeline !' }

    }

}

