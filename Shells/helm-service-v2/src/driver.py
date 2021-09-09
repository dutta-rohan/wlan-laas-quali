import os
import git
import shutil
import subprocess
import tempfile
import requests
import urllib.request
from distutils.dir_util import copy_tree

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes


URL_TEMPLATE = 'https://sec-{}.cicd.lab.wlan.tip.build/ping'
WINDOWS_LINE_ENDING = b'\r\n'
UNIX_LINE_ENDING = b'\n'


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

    def helm_install(self, context):
        api_session = CloudShellSessionContext(context).get_api()
        res_id = context.reservation.reservation_id
        partial_namespace = res_id.split('-')[0]
        namespace = 'ucentral-' + partial_namespace

        service_resource = HelmServiceV2.create_from_context(context)

        api_session.WriteMessageToReservationOutput(res_id, "Installing Helm Chart from: {}...".format(
                                                            service_resource.github_repo_url))

        # Get AWS creds from AWS EC2 resource
        aws_resource = api_session.FindResources(resourceModel='AWS EC2').Resources[0]
        access_key_id = api_session.GetAttributeValue(aws_resource.Name, 'AWS Access Key ID').Value
        secret_access_key = api_session.GetAttributeValue(aws_resource.Name, 'AWS Secret Access Key').Value
        region = api_session.GetAttributeValue(aws_resource.Name, 'Region').Value

        # Set environment variables for aws cli configuration
        os.environ['AWS_ACCESS_KEY_ID'] = api_session.DecryptPassword(access_key_id).Value
        os.environ['AWS_SECRET_ACCESS_KEY'] = api_session.DecryptPassword(secret_access_key).Value
        os.environ['AWS_DEFAULT_REGION'] = region

        # Clone Git Repo to temporary directory
        working_dir = tempfile.mkdtemp()
        git.Repo.clone_from(service_resource.github_repo_url, working_dir, branch=service_resource.github_repo_branch, depth=1)

        # Copy certs from local folder to temporary git repo certs directory
        temp_path = os.path.join(working_dir, service_resource.github_repo_path_to_chart, 'resources')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        temp_path = os.path.join(working_dir, service_resource.github_repo_path_to_chart, 'resources', 'certs')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        local_cert_path = os.path.join('/Quali', 'helm', 'certs')
        temp_cert_path = os.path.join(working_dir, service_resource.github_repo_path_to_chart, 'resources', 'certs')
        copy_tree(local_cert_path, temp_cert_path)

        # Get windows batch file for Helm Install and enter secrets
        response = requests.get(service_resource.helm_deploy_script_url)

        temp = str(response.content.decode('utf-8')).replace('{NAMESPACE}', partial_namespace)

        temp = temp.replace('{AWS_ACCESS_KEY_ID}', api_session.DecryptPassword(access_key_id).Value)
        temp = temp.replace('{AWS_SECRET_ACCESS_KEY}', api_session.DecryptPassword(secret_access_key).Value)
        temp = temp.replace('{AWS_DEFAULT_REGION}', region)
        temp = temp.replace('{RTTY_TOKEN}', api_session.DecryptPassword(service_resource.rtty_token).Value)
        temp = temp.replace('{UCENTRALGW_AUTH_USERNAME}', api_session.DecryptPassword(service_resource.ucentralgw_auth_username).Value)
        temp = temp.replace('{UCENTRALGW_AUTH_PASSWORD}', api_session.DecryptPassword(service_resource.ucentralgw_auth_password).Value)
        temp = temp.replace('{UCENTRALFMS_S3_SECRET}', api_session.DecryptPassword(service_resource.ucentralfms_s3_secret).Value)
        temp = temp.replace('{UCENTRALFMS_S3_KEY}', api_session.DecryptPassword(service_resource.ucentralfms_s3_key).Value)
        #temp = temp.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        script_path = os.path.join(working_dir, service_resource.github_repo_path_to_chart, 'helmDeploy.sh')

        fout = open(script_path, "wt")
        fout.write(temp)
        fout.close()
        os.chmod(script_path, 0o777)

        chart_path = os.path.join(working_dir, service_resource.github_repo_path_to_chart)

        result = subprocess.Popen('dos2unix helmDeploy.sh', cwd=chart_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result.communicate(' ')
        if errors:
            api_session.WriteMessageToReservationOutput(res_id, repr(errors))

        # Run batch file in temp directory
        result = subprocess.Popen('./helmDeploy.sh', cwd=chart_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        namespace = 'ucentral-' + partial_namespace

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
        command2 = ' '.join(['helm del tip-ucentral --namespace', namespace])
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