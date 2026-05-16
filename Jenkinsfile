pipeline {
    agent any
    environment {
        APP_NAME = "flask-app"
        APP_PORT = "5000"
        DATA_PATH = "/home/vagrant/app/data"
        VM_IP = "192.168.56.10"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Tests') {
            steps {
                sh 'python3 -m pytest test_app.py -v'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${APP_NAME} .'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker stop ${APP_NAME} || true'
                sh 'docker rm ${APP_NAME} || true'
                sh 'docker run -d --name ${APP_NAME} --restart=always -p ${APP_PORT}:5000 -v ${DATA_PATH}:/app/data ${APP_NAME}'
            }
        }
        stage('Verify') {
            steps {
                sh 'sleep 5'
                sh 'curl -f http://${VM_IP}:${APP_PORT}/health'
            }
        }
    }
    post {
        success { echo 'Deploiement reussi !' }
        failure { echo 'Echec du pipeline !' }
    }
}
