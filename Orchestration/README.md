# Orchestration

## Custom Setup V2
This Setup script was designed using the Basic Labs as testing resources. The workflow for the Setup script is as follows:
* Execute Helm install command on Helm Service within Sandbox
* Redirect all APs within the Sandbox to the SDK that was deployed
    * The namespace for the URL is 'ucentral-{8 characters from sandbox id}'
* Run command to Factory Reset APs in order to initiate communication with SDK
* Default CloudShell setup procedures (Reserving Basic Lab resources)

## Custom Teardown V2
This Teardown script was designed using the Basic Labs as testing resources. The workflow for the Teardown script is as follows:
* Execute Helm uninstall command on Helm Service within Sandbox
* Redirect all APs within the Sandbox to default URl
    * The defaulty namespace is 'ucentral-qa01'
* Run command to Factory Reset APs in order to initiate communication with default SDK
* Default CloudShell Teardown procedures (Release Basic Lab resources back to pool)