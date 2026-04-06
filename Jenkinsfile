pipeline {
    agent any
 
    environment {
        ACR_NAME       = "airqualityacr"
        ACR_LOGIN_URL  = "airqualityacr.azurecr.io"
        IMAGE_NAME     = "airquality-app"
        IMAGE_TAG      = "latest"
        RESOURCE_GROUP = "rg-dut-lab"
        AKS_CLUSTER    = "hibanourahajar"
    }
 
    triggers {
        // Auto-run on every push to GitHub
        githubPush()
    }
 
    stages {
 
        // ─────────────────────────────
        // 1. PULL CODE FROM GITHUB
        // ─────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
 
        // ─────────────────────────────
        // 2. BUILD DOCKER IMAGE
        // ─────────────────────────────
        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${ACR_LOGIN_URL}/${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }
 
        // ─────────────────────────────
        // 3. PUSH TO AZURE CONTAINER REGISTRY
        // Uses a permanent ACR token stored in Jenkins credentials (ID: acr-token)
        // This avoids MFA expiry issues with az acr login
        // ─────────────────────────────
        stage('Push to ACR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'acr-token', usernameVariable: 'ACR_USER', passwordVariable: 'ACR_PASS')]) {
                    sh """
                        echo $ACR_PASS | docker login ${ACR_LOGIN_URL} -u $ACR_USER --password-stdin
                        docker push ${ACR_LOGIN_URL}/${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }
 
        // ─────────────────────────────
        // 4. RUN KUBERNETES JOB (process.py)
        // ─────────────────────────────
        stage('Run Kubernetes Job') {
            steps {
                sh """
                    # Connect kubectl to AKS
                    az aks get-credentials --resource-group ${RESOURCE_GROUP} --name ${AKS_CLUSTER} --overwrite-existing
 
                    # Delete old job if exists
                    kubectl delete job airquality-job --ignore-not-found=true
 
                    # Apply and run the job
                    kubectl apply -f job.yaml
 
                    # Wait for job to complete (max 5 minutes)
                    kubectl wait --for=condition=complete job/airquality-job --timeout=300s
                """
            }
        }
 
        // ─────────────────────────────
        // 5. RESTART DASHBOARD
        // ─────────────────────────────
        stage('Restart Dashboard') {
            steps {
                sh """
                    # Copy latest dashboard.py from repo to home
                    cp dashboard.py /home/hibanoura/dashboard.py
 
                    # Kill any running streamlit instance
                    pkill -f "streamlit run" || true
 
                    # Wait a moment for port to free
                    sleep 2
 
                    # Start dashboard in background with AZURE_CONN_STR
                    nohup /home/hibanoura/myenv/bin/streamlit run /home/hibanoura/dashboard.py \
                        --server.port 8501 \
                        --server.headless true \
                        > /tmp/streamlit.log 2>&1 &
 
                    echo "✅ Dashboard restarted at http://4.235.120.51:8501"
                """
            }
        }
    }
 
    // ─────────────────────────────
    // NOTIFICATIONS
    // ─────────────────────────────
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
    }
}
