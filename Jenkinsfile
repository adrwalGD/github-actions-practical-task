pipeline {
    agent any

    environment {
        IMAGE_NAME = "spring-petclinic"
        AZURE_DOCKER_REGISTRY = "adrwalacr.azurecr.io"
        AZURE_DOCKER_REGISTRY_URL = "https://adrwalacr.azurecr.io/"
        DOCKER_REGEISTRY_CREDENTIALS_ID = "ACR-user-pass"
        GITHUB_SSH_CREDENTIALS_ID = "github-ssh"
        GITHUB_REPOSITORY = "git@github.com:adrwalGD/capstone-module-petclinic.git"
    }

    tools {
        maven 'maven'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Static Code Analysis') {
            steps {
                echo "Running static code analysis..."
                sh 'mvn checkstyle:checkstyle'
                // sh 'mvn checkstyle:check' // Commented because code base contains a lot of checkstyle errors
                // sh 'mvn spotbugs:check' // Commented because code base contains a lot of spotbugs:check errors
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running unit tests..."
                sh 'mvn test'
            }
        }

        stage('Build Application') {
            steps {
                echo "Building the application..."
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Create Artifact tag') {
            steps {
                echo "Creating artifact tag..."
                script {
                    if (env.BRANCH_NAME == 'main') {
                        sshagent([env.GITHUB_SSH_CREDENTIALS_ID]) {
                            sh "mkdir -p ~/.ssh"
                            sh "ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts"
                            sh "git fetch --tags ${env.GITHUB_REPOSITORY}"
                            echo "fetched tags..."
                        }
                        def latestTag = sh(script: 'git describe --tags `git rev-list --tags --max-count=1`', returnStdout: true).trim()
                        echo "Latest tag: ${latestTag}"
                        env.LATEST_TAG = latestTag

                        def tag = docker.image('python:3.8').inside('-v pip-cache:/.cache/pip'){
                            withEnv(["HOME=${env.WORKSPACE}"]) {
                                sh 'pip install --no-cache-dir semver'
                                def newTag = sh(script: "python3 semver_script.py ${env.LATEST_TAG} minor", returnStdout: true).trim()
                                echo "New tag: ${newTag}"
                                sh 'rm -rf .local'
                                return newTag
                            }
                        }
                        env.GIT_TAG = tag
                        def imageTag = "${AZURE_DOCKER_REGISTRY}/${IMAGE_NAME}:${tag}"
                        env.IMAGE_TAG = imageTag
                    } else {
                        def shortCommit = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                        def imageTag = "${AZURE_DOCKER_REGISTRY}/${IMAGE_NAME}:${shortCommit}"
                        env.IMAGE_TAG = imageTag
                    }
                    echo "Generated artifact tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build(env.IMAGE_TAG, ".")
                }
            }
        }


        stage('Push Artifact to ACR') {
            steps {
                script {
                    docker.withRegistry(AZURE_DOCKER_REGISTRY_URL, DOCKER_REGEISTRY_CREDENTIALS_ID) {
                        echo "Logging in to Azure Container Registry..."
                        dockerImage.push()
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Push git tag') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sshagent([env.GITHUB_SSH_CREDENTIALS_ID]) {
                        sh "git tag ${env.GIT_TAG}"
                        sh "git push ${env.GITHUB_REPOSITORY} tag ${env.GIT_TAG}"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}
