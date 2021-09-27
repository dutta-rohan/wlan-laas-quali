# Shells

## AP Shell

## Controller VM

## Helm Service V2
This Helm Service V2 shell contains the logic to deploy and tear down an instance of the Cloud SDK.<br>
When placing the Service into a Sandbox certain config and Secret values are required:
* Config:
    * Github Repo URL
    * Github Repo Branch
    * Github Path to install script
* Secrets
    * RTTY_TOKEN
    * UCENTRALFMS_S3_KEY
    * UCENTRALFMS_S3_SECRET
    * UCENTRALGW_AUTH_USERNAME
    * UCENTRALGW_AUTH_PASSWORD

#### helm_install command
The Helm install command will take a number of inputs in order deploy the correct release of the SDK.
The created namepspace of the SDK will be of the format 'ucentral-{First 8 characters of Sandbox id}'

* Required inputs
    * chart_version
    * ucentralgw_version
    * ucentralsec_version
    * ucentralfms_version
    * ucentralgwui_version
    
Install flow is as follows:
* Clone Github Repo to a temporary directory
* Copy/Create the required certificates
* Gather required config/secret values from itself and other CloudShell resources
* Update install script with gathered values
* Run updated install script

#### helm_uninstall command
The Helm uninstall command will clean up the SDK that was deployed by the service in the current Sandbox. No inputs required.

Uninstall flow is as follows:
* Gather required config/secret values from itself and other CloudShell resources
* Run command to delete SDk release from the namespace that was created
* Run command to delete the namespace itself

## RF
The RF shell does not contain any custom automation code.
It is used to hold information/attributes that can otherwise be used from the CloudShell orchestration scripts or pytest runs.

## TG
The TG shell does not contain any custom automation code.
It is used to hold information/attribtues that can otherwise be used from the CloudShell orchestration scripts or pytest runs.