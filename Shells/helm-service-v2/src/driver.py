import os
import git
import shutil
import subprocess
import tempfile
from distutils.dir_util import copy_tree

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)


class HelmServiceV2Driver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def helm_install(self, context, chart_version, owgw_version, owsec_version, owfms_version, owgwui_version, owprov_version, owprovui_version):
        api_session = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        partial_namespace = res_id.split('-')[0]

        service_resource = HelmServiceV2.create_from_context(context)

        api_session.WriteMessageToReservationOutput(res_id, "Downloading Helm Install Script: {}".format(service_resource.github_repo_url))

        # Get AWS creds from AWS EC2 resource
        aws_resource = api_session.FindResources(resourceModel='AWS EC2').Resources[0]
        access_key_id = api_session.GetAttributeValue(aws_resource.Name, 'AWS Access Key ID').Value
        secret_access_key = api_session.GetAttributeValue(aws_resource.Name, 'AWS Secret Access Key').Value
        region = api_session.GetAttributeValue(aws_resource.Name, 'Region').Value

        # Clone Git Repo to temporary directory
        working_dir = tempfile.mkdtemp()
        git.Repo.clone_from(service_resource.github_repo_url, working_dir, branch=service_resource.github_repo_branch, depth=1)

        github_path = os.path.join(*(service_resource.github_repo_path_to_chart.split('/')))
        cert_path = os.path.join(working_dir, github_path)
        script_path = os.path.join(cert_path, 'deploy.sh')

        # Copy certs from local directory to git repo folder
        local_cert_path = os.path.join('/Quali', 'helm', 'certs')
        copy_tree(local_cert_path, cert_path)

        # Set environment variables for aws cli configuration
        os.environ['AWS_ACCESS_KEY_ID'] = api_session.DecryptPassword(access_key_id).Value
        os.environ['AWS_SECRET_ACCESS_KEY'] = api_session.DecryptPassword(secret_access_key).Value
        os.environ['AWS_DEFAULT_REGION'] = region

        # Set environment variables for script run
        os.environ['NAMESPACE'] = partial_namespace
        os.environ['DEPLOY_METHOD'] = 'git'
        os.environ['CHART_VERSION'] = chart_version

        os.environ['OWGW_VERSION'] = owgw_version
        os.environ['OWGWUI_VERSION'] = owgwui_version
        os.environ['OWSEC_VERSION'] = owsec_version
        os.environ['OWFMS_VERSION'] = owfms_version
        #os.environ['UCENTRALGW_VERSION'] = ucentralgw_version
        #os.environ['UCENTRALGWUI_VERSION'] = ucentralgwui_version
        #os.environ['UCENTRALSEC_VERSION'] = ucentralsec_version
        #os.environ['UCENTRALFMS_VERSION'] = ucentralfms_version

        os.environ['VALUES_FILE_LOCATION'] = 'values.ucentral-qa.yaml'
        os.environ['RTTY_TOKEN'] = api_session.DecryptPassword(service_resource.rtty_token).Value

        os.environ['OWGW_AUTH_USERNAME'] = api_session.DecryptPassword(service_resource.owgw_auth_username).Value
        os.environ['OWGW_AUTH_PASSWORD'] = api_session.DecryptPassword(service_resource.owgw_auth_password).Value
        os.environ['OWFMS_S3_SECRET'] = api_session.DecryptPassword(service_resource.owfms_s3_secret).Value
        os.environ['OWFMS_S3_KEY'] = api_session.DecryptPassword(service_resource.owfms_s3_key).Value
        #os.environ['UCENTRALGW_AUTH_USERNAME'] = api_session.DecryptPassword(service_resource.ucentralgw_auth_username).Value
        #os.environ['UCENTRALGW_AUTH_PASSWORD'] = api_session.DecryptPassword(service_resource.ucentralgw_auth_password).Value
        #os.environ['UCENTRALFMS_S3_SECRET'] = api_session.DecryptPassword(service_resource.ucentralfms_s3_secret).Value
        #os.environ['UCENTRALFMS_S3_KEY'] = api_session.DecryptPassword(service_resource.ucentralfms_s3_key).Value

        os.environ['CERT_LOCATION'] = 'cert.pem'
        os.environ['KEY_LOCATION'] = 'key.pem'

        os.chmod(script_path, 0o777)

        result = subprocess.Popen('dos2unix deploy.sh', cwd=cert_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result.communicate(' ')
        if errors:
            api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        # Run batch file in temp directory
        result = subprocess.Popen('./deploy.sh', cwd=cert_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result.communicate(' ')
        if errors:
            api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        # Delete temp folder
        shutil.rmtree(working_dir, onerror=onerror)

        api_session.WriteMessageToReservationOutput(res_id, "Helm Install Successful.")

    def helm_uninstall(self, context):
        api_session = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        partial_namespace = res_id.split('-')[0]
        namespace = 'openwifi-' + partial_namespace

        api_session.WriteMessageToReservationOutput(res_id, "Executing Helm Uninstall...")

        # Get AWS creds from AWS EC2 resource
        aws_resource = api_session.FindResources(resourceModel='AWS EC2').Resources[0]
        access_key_id = api_session.GetAttributeValue(aws_resource.Name, 'AWS Access Key ID').Value
        secret_access_key = api_session.GetAttributeValue(aws_resource.Name, 'AWS Secret Access Key').Value
        region = api_session.GetAttributeValue(aws_resource.Name, 'Region').Value

        # Set environment variables for aws cli configuration
        os.environ['AWS_ACCESS_KEY_ID'] = api_session.DecryptPassword(access_key_id).Value
        os.environ['AWS_SECRET_ACCESS_KEY'] = api_session.DecryptPassword(secret_access_key).Value
        os.environ['AWS_DEFAULT_REGION'] = region

        # Update Kubeconfig prior to helm install
        command1 = 'aws eks update-kubeconfig --name tip-wlan-main'
        result1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result1.communicate(' ')
        #if len(errors) > 0:
        #    api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        # Helm delete/uninstall
        command2 = ' '.join(['helm del tip-openwifi --namespace', namespace])
        result2 = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result2.communicate(' ')
        #if len(errors) > 0:
        #    api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        # Delete namespace
        command3 = ' '.join(['kubectl delete namespace', namespace])
        result3 = subprocess.Popen(command3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result3.communicate(' ')
        #if len(errors) > 0:
        #    api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        api_session.WriteMessageToReservationOutput(res_id, "Helm Uninstall Successful.")