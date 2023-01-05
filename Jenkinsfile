#!/usr/bin/env groovy

pipeline {
    environment {
        OTP_CDO_DATETIME = "${new Date().format("yyyyMMddHHmm")}"
    }
    options {
        timeout(time: 10, unit: "MINUTES")
        buildDiscarder(logRotator(daysToKeepStr: "5", artifactDaysToKeepStr: "5"))
        timestamps()
    }
    agent {
        label "cdo-python-agent"
    }
    parameters {
        string(name: 'PROJECT_NAMES', defaultValue: '', description: 'Required. The SonarQube project(s) name.')
        string(name: 'RO_EMAILS', defaultValue: '', description: 'List of email addresses of the users to add to project(s) with RO permission. Separated by comma or space.')
        string(name: 'RW_EMAILS', defaultValue: '', description: 'List of email addresses of the users to add to project(s) with RW permission. Separated by comma or space.')
        string(name: 'RO_GROUPS', defaultValue: '', description: 'List of groups to add to project(s) with RO permission. Separated by comma or space.')
        string(name: 'RW_GROUPS', defaultValue: '', description: 'List of groups to add to project(s) with RW permission. Separated by comma or space.')
    }
    stages {
        stage("Prepare") {
            steps {
                sh """
mkdir -p ~/.config/pip/
echo "[global]
index = https://otpnexus.hu/repository/anonymous-proxy-py-pypi.org/pypi
index-url = https://otpnexus.hu/repository/anonymous-proxy-py-pypi.org/simple
timeout = 10
retries = 1" > ~/.config/pip/pip.conf
                """
                sh "pip install -r requirements.txt"
            }
        }
        stage("SonarQube Permission ") {
            steps {
                script{
                    def extraArgs = []
                    if(params.PROJECT_NAMES){
                        extraArgs.add("--project_names \"${PROJECT_NAMES}\"")
                    }
                    if(params.RO_EMAILS){
                        extraArgs.add("--ro_emails \"${params.RO_EMAILS}\"")
                    }
                    if(params.RW_EMAILS){
                        extraArgs.add("--rw_emails \"${params.RW_EMAILS}\"")
                    }
                    if(params.RO_GROUPS){
                        extraArgs.add("--ro_groups \"${params.RO_GROUPS}\"")
                    }
                    if(params.RW_GROUPS){
                        extraArgs.add("--rw_groups \"${params.RW_GROUPS}\"")
                    }
                    withCredentials( [string(credentialsId: "SONARQUBE_ONBOARDING", variable: 'TOKEN')]) {
                        sh('python3 bin/sonar.py $TOKEN ' + """ \
                                ${extraArgs.join(' ')}"""
                        )
                    }
                }
            }
        }
    }
}