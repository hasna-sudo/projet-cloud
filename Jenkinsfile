pipeline {
    agent any

    environment {
        APP_NAME = "flask-app"
        STAGING_URL = "http://192.168.56.10:5000"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'pytest tests/'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${APP_NAME}:${BUILD_NUMBER} .'
            }
        }

        stage('Container Security Scan') {
            steps {
                sh 'trivy image ${APP_NAME}:${BUILD_NUMBER}'
            }
        }

        stage('Deploy Staging') {
            steps {
                sh 'docker stop staging-app || true'
                sh 'docker rm staging-app || true'

                sh '''
                    docker run -d \
                    --name staging-app \
                    -p 5000:5000 \
                    ${APP_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh 'sleep 5'
                sh 'curl -f http://localhost:${APP_PORT}/health'
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                    docker run --rm \
                    --network host \
                    -v $(pwd):/zap/wrk/:rw \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py \
                    -t ${STAGING_URL} \
                    -r zap-report.html \
                    -l WARN
                '''
            }
        }

        stage('Deploy Production') {
            steps {
                echo "Validation OK, production deploy"
            }
        }

    }
}
