from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.teardown.default_teardown_orchestrator import DefaultTeardownWorkflow


def helm_uninstall(sandbox, components):
    for each in sandbox.automation_api.GetReservationDetails(sandbox.id).ReservationDescription.Services:
        if each.ServiceName == 'Helm Service V2':
            sandbox.automation_api.ExecuteCommand(sandbox.id, each.Alias, "Service", 'helm_uninstall')


sandbox = Sandbox()

DefaultTeardownWorkflow().register(sandbox)
sandbox.workflow.add_to_teardown(helm_uninstall, [])

sandbox.execute_teardown()
