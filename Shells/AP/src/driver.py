import os
import git
import shutil
import subprocess
import tempfile

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext

from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from data_model import *  # run 'shellfoundry generate' to generate data model classes

GITHUB_REPO = 'https://github.com/Telecominfraproject/wlan-testing.git'
GITHUB_REPO_Branch = 'master'
GITHUB_REPO_NAME = 'wlan-testing'
PDU_REPO_PATH = 'tools'
PDU_SCRIPT_NAME = 'pdu_automation.py'

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


class ApDriver (ResourceDriverInterface):

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

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model

        resource = Ap.create_from_context(context)
        # resource.vendor = 'specify the shell vendor'
        # resource.model = 'specify the shell model'

        for i in range(2):
            port = ResourcePort('connector' + str(i))
            resource.add_sub_resource(str(i), port)

        return resource.create_autoload_details()

        '''
        resource = Ap.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        # return AutoLoadDetails([], [])

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
      """
      Saves the Shell state and returns a description of the saved artifacts and information
      This command is intended for API use only by sandbox orchestration scripts to implement
      a save and restore workflow
      :param ResourceCommandContext context: the context object containing resource and reservation info
      :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
      :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
      :param str custom_params: Set of custom parameters for the save operation
      :return: SavedResults serialized as JSON
      :rtype: OrchestrationSaveResult
      """

      # See below an example implementation, here we use jsonpickle for serialization,
      # to use this sample, you'll need to add jsonpickle to your requirements.txt file
      # The JSON schema is defined at:
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
      # You can find more information and examples examples in the spec document at
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
      '''
            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.

            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.
            identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')

            orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)

            saved_artifacts_info = OrchestrationSavedArtifactInfo(
                resource_name="some_resource",
                created_date=created_date,
                restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                saved_artifact=orchestration_saved_artifact)

            return OrchestrationSaveResult(saved_artifacts_info)
      '''
      pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    # </editor-fold>

    def powerOffOtherAPs(self, context, cancellation_context):
        res_id = context.reservation.reservation_id

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as api_session:

                other_aps = []

                for each in api_session.FindResources(resourceModel='Ap').Resources:
                    if context.resource.name != each.Name and context.resource.name.split(' - ')[1] == each.Name .split(' - ')[1]:
                        other_aps.append(each)

                if other_aps:
                    for each in other_aps:
                        hostname = context.resource.attributes["{}.PDU Host".format(each.Model)]
                        username = context.resource.attributes["{}.PDU User".format(each.Model)]
                        password = context.resource.attributes["{}.PDU Password".format(each.Model)]
                        port = context.resource.attributes["{}.PDU Port".format(each.Model)]

                        working_dir = tempfile.mkdtemp()
                        git.Repo.clone_from(GITHUB_REPO, working_dir, branch=GITHUB_REPO_Branch, depth=1)

                        tools_path = os.path.join(working_dir, GITHUB_REPO_NAME, PDU_REPO_PATH)
                        script_path = os.path.join(working_dir, GITHUB_REPO_NAME, PDU_REPO_PATH, PDU_SCRIPT_NAME)

                        cmd = "python3 {} --host {} --user {} --password {} --action off --port '{}'".format(PDU_SCRIPT_NAME, hostname, username, password, port)

                        result = subprocess.Popen(cmd, cwd=tools_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, errors = result.communicate(' ')
                        if errors:
                            api_session.WriteMessageToReservationOutput(res_id, repr(errors))

                        # Delete temp folder
                        shutil.rmtree(working_dir, onerror=onerror)

                else:
                    api_session.WriteMessageToReservationOutput(res_id, 'No APs to power off.')

    def powerOnOtherAPs(self, context, cancellation_context):
        res_id = context.reservation.reservation_id

        with LoggingSessionContext(context) as logger, ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as api_session:

                other_aps = []

                for each in api_session.FindResources(resourceModel='Ap').Resources:
                    if context.resource.name != each.Name and context.resource.name.split(' - ')[1] == each.Name .split(' - ')[1]:
                        other_aps.append(each)

                if other_aps:
                    for each in other_aps:
                        hostname = context.resource.attributes["{}.PDU Host".format(each.Model)]
                        username = context.resource.attributes["{}.PDU User".format(each.Model)]
                        password = context.resource.attributes["{}.PDU Password".format(each.Model)]
                        port = context.resource.attributes["{}.PDU Port".format(each.Model)]

                        working_dir = tempfile.mkdtemp()
                        git.Repo.clone_from(GITHUB_REPO, working_dir, branch=GITHUB_REPO_Branch, depth=1)

                        tools_path = os.path.join(working_dir, GITHUB_REPO_NAME, PDU_REPO_PATH)
                        script_path = os.path.join(working_dir, GITHUB_REPO_NAME, PDU_REPO_PATH, PDU_SCRIPT_NAME)

                        cmd = "python3 {} --host {} --user {} --password {} --action on --port '{}'".format(PDU_SCRIPT_NAME, hostname, username, password, port)

                        result = subprocess.Popen(cmd, cwd=tools_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, errors = result.communicate(' ')
                        if errors:
                            api_session.WriteMessageToReservationOutput(res_id, repr(errors))

                        # Delete temp folder
                        shutil.rmtree(working_dir, onerror=onerror)

                else:
                    api_session.WriteMessageToReservationOutput(res_id, 'No APs to power on.')
