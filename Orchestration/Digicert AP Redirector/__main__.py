import os
import shutil
import requests
import tempfile
import subprocess
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers


SCRIPT_URL = 'https://raw.githubusercontent.com/Telecominfraproject/wlan-pki-cert-scripts/master/digicert-change-ap-redirector.sh'
SCRIPT_URL2 = 'https://raw.githubusercontent.com/Telecominfraproject/wlan-pki-cert-scripts/master/digicert-library.sh'
SCRIPT_URL3 = 'https://raw.githubusercontent.com/Telecominfraproject/wlan-pki-cert-scripts/master/digicert-config.sh'
URL_TEMPLATE = 'gw-ucentral-{}.cicd.lab.wlan.tip.build'


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


def main():
    sandbox = Sandbox()
    resource = helpers.get_resource_context_details()
    redirect_url = URL_TEMPLATE.format(sandbox.id.split('-')[0])

    working_dir = tempfile.mkdtemp()

    script_path = os.path.join(working_dir, 'digicert-change-ap-redirector.sh')
    script_path2 = os.path.join(working_dir, 'digicert-library.sh')
    script_path3 = os.path.join(working_dir, 'digicert-config.sh')

    response = requests.get(SCRIPT_URL)
    response2 = requests.get(SCRIPT_URL2)
    response3 = requests.get(SCRIPT_URL3)

    temp = str(response.content.decode('utf-8'))
    fout = open(script_path, "wt")
    fout.write(temp)
    fout.close()
    os.chmod(script_path, 0o777)

    temp = str(response2.content.decode('utf-8'))
    fout = open(script_path2, "wt")
    fout.write(temp)
    fout.close()
    os.chmod(script_path2, 0o777)

    temp = str(response3.content.decode('utf-8'))
    fout = open(script_path3, "wt")
    fout.write(temp)
    fout.close()
    os.chmod(script_path3, 0o777)

    result = subprocess.Popen('dos2unix digicert-change-ap-redirector.sh', cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = result.communicate(' ')
    if errors:
        sandbox.automation_api.WriteMessageToReservationOutput(sandbox.id, repr(errors))

    result = subprocess.Popen('dos2unix digicert-library.sh', cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = result.communicate(' ')
    if errors:
        sandbox.automation_api.WriteMessageToReservationOutput(sandbox.id, repr(errors))

    result = subprocess.Popen('dos2unix digicert-config.sh', cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = result.communicate(' ')
    if errors:
        sandbox.automation_api.WriteMessageToReservationOutput(sandbox.id, repr(errors))

    os.environ['DIGICERT_API_KEY'] = sandbox.automation_api.DecryptPassword(resource.attributes['Digicert API Key']).Value

    result = subprocess.Popen('./digicert-change-ap-redirector.sh {} {}'.format(resource.attributes['Ap.Serial Number'], redirect_url), cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = result.communicate(' ')
    if errors:
        sandbox.automation_api.WriteMessageToReservationOutput(sandbox.id, repr(errors))

    shutil.rmtree(working_dir, onerror=onerror)

    sandbox.automation_api.WriteMessageToReservationOutput(sandbox.id, "Digicert AP Redirect Successful.")


if __name__ == "__main__":
    main()
