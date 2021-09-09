#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
export AWS_DEFAULT_REGION={AWS_DEFAULT_REGION}
aws eks update-kubeconfig --name tip-wlan-main
helm plugin install https://github.com/aslafy-z/helm-git --version 0.10.0
sed -i '/wlan-cloud-ucentralgw@/s/ref=.*/ref='master'\"/g' Chart.yaml
sed -i '/wlan-cloud-ucentralgw-ui@/s/ref=.*/ref='main'\"/g' Chart.yaml
sed -i '/wlan-cloud-ucentralsec@/s/ref=.*/ref='main'\"/g' Chart.yaml
sed -i '/wlan-cloud-ucentralfms@/s/ref=.*/ref='main'\"/g' Chart.yaml
export UCENTRALGW_VERSION_TAG=$(echo master | tr '/' '-')
export UCENTRALGWUI_VERSION_TAG=$(echo main | tr '/' '-')
export UCENTRALSEC_VERSION_TAG=$(echo main | tr '/' '-')
export UCENTRALFMS_VERSION_TAG=$(echo main | tr '/' '-')
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm dependency update
helm upgrade --install --create-namespace \
  --namespace ucentral-{NAMESPACE} --wait --timeout 20m \
  -f /home/centos/Quali/helm/values/values.ucentral-qa.yaml \
  --set ucentralgw.configProperties."rtty\.token"={RTTY_TOKEN} \
  --set ucentralsec.configProperties."authentication\.default\.username"={UCENTRALGW_AUTH_USERNAME} \
  --set ucentralsec.configProperties."authentication\.default\.password"={UCENTRALGW_AUTH_PASSWORD} \
  --set rttys.config.token={RTTY_TOKEN} \
  --set ucentralfms.configProperties."s3\.secret"={UCENTRALFMS_S3_SECRET} \
  --set ucentralfms.configProperties."s3\.key"={UCENTRALFMS_S3_KEY} \
  --set ucentralgw.services.ucentralgw.annotations."external-dns\.alpha\.kubernetes\.io/hostname"=gw-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralgw.configProperties."ucentral\.fileuploader\.host\.0\.name"=gw-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralgw.configProperties."rtty\.server"=rtty-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralgw.configProperties."ucentral\.system\.uri\.public"=https://gw-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:16002 \
  --set ucentralgw.configProperties."ucentral\.system\.uri\.private"=https://gw-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:17002 \
  --set ucentralgw.configProperties."ucentral\.system\.uri\.ui"=https://webui-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralsec.services.ucentralsec.annotations."external-dns\.alpha\.kubernetes\.io/hostname"=sec-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralsec.configProperties."ucentral\.system\.uri\.public"=https://sec-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:16001 \
  --set ucentralsec.configProperties."ucentral\.system\.uri\.private"=https://sec-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:17001 \
  --set ucentralsec.configProperties."ucentral\.system\.uri\.ui"=https://webui-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set rttys.services.rttys.annotations."external-dns\.alpha\.kubernetes\.io/hostname"=rtty-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralgwui.ingresses.default.annotations."external-dns\.alpha\.kubernetes\.io/hostname"=webui-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralgwui.ingresses.default.hosts={webui-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build} \
  --set ucentralgwui.public_env_variables.DEFAULT_UCENTRALSEC_URL=https://sec-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:16001 \
  --set ucentralfms.services.ucentralfms.annotations."external-dns\.alpha\.kubernetes\.io/hostname"=fms-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set ucentralfms.configProperties."ucentral\.system\.uri\.public"=https://fms-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:16004 \
  --set ucentralfms.configProperties."ucentral\.system\.uri\.private"=https://fms-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build:17004 \
  --set ucentralfms.configProperties."ucentral\.system\.uri\.ui"=https://webui-ucentral-{NAMESPACE}.cicd.lab.wlan.tip.build \
  --set-file ucentralgw.certs."restapi-cert\.pem"=/home/centos/Quali/helm/certs/cert.pem \
  --set-file ucentralgw.certs."restapi-key\.pem"=/home/centos/Quali/helm/certs/key.pem \
  --set-file ucentralgw.certs."websocket-cert\.pem"=/home/centos/Quali/helm/certs/cert.pem \
  --set-file ucentralgw.certs."websocket-key\.pem"=/home/centos/Quali/helm/certs/key.pem \
  --set-file rttys.certs."restapi-cert\.pem"=/home/centos/Quali/helm/certs/cert.pem \
  --set-file rttys.certs."restapi-key\.pem"=/home/centos/Quali/helm/certs/key.pem \
  --set-file ucentralsec.certs."restapi-cert\.pem"=/home/centos/Quali/helm/certs/cert.pem \
  --set-file ucentralsec.certs."restapi-key\.pem"=/home/centos/Quali/helm/certs/key.pem \
  --set-file ucentralfms.certs."restapi-cert\.pem"=/home/centos/Quali/helm/certs/cert.pem \
  --set-file ucentralfms.certs."restapi-key\.pem"=/home/centos/Quali/helm/certs/key.pem \
  --set ucentralgw.images.ucentralgw.tag=master \
  --set ucentralgwui.images.ucentralgwui.tag=main \
  --set ucentralsec.images.ucentralsec.tag=main \
  --set ucentralfms.images.ucentralfms.tag=main \
  tip-ucentral .