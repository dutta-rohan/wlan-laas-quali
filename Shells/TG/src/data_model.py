from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class Trafficgenerator(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Trafficgenerator'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype Trafficgenerator
        """
        result = Trafficgenerator(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'Trafficgenerator'

    @property
    def tg_model(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.TG Model'] if 'Trafficgenerator.TG Model' in self.attributes else None

    @tg_model.setter
    def tg_model(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.TG Model'] = value

    @property
    def tg_port(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.TG Port'] if 'Trafficgenerator.TG Port' in self.attributes else None

    @tg_port.setter
    def tg_port(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.TG Port'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Serial Number'] if 'Trafficgenerator.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.Serial Number'] = value

    @property
    def user(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.User'] if 'Trafficgenerator.User' in self.attributes else None

    @user.setter
    def user(self, value):
        """
        User with administrative privileges
        :type value: str
        """
        self.attributes['Trafficgenerator.User'] = value

    @property
    def password(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.Password'] if 'Trafficgenerator.Password' in self.attributes else None

    @password.setter
    def password(self, value):
        """
        
        :type value: string
        """
        self.attributes['Trafficgenerator.Password'] = value

    @property
    def enable_password(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.Enable Password'] if 'Trafficgenerator.Enable Password' in self.attributes else None

    @enable_password.setter
    def enable_password(self, value):
        """
        The enable password is required by some CLI protocols such as Telnet and is required according to the device configuration.
        :type value: string
        """
        self.attributes['Trafficgenerator.Enable Password'] = value

    @property
    def power_management(self):
        """
        :rtype: bool
        """
        return self.attributes['Trafficgenerator.Power Management'] if 'Trafficgenerator.Power Management' in self.attributes else None

    @power_management.setter
    def power_management(self, value=True):
        """
        Used by the power management orchestration, if enabled, to determine whether to automatically manage the device power status. Enabled by default.
        :type value: bool
        """
        self.attributes['Trafficgenerator.Power Management'] = value

    @property
    def sessions_concurrency_limit(self):
        """
        :rtype: float
        """
        return self.attributes['Trafficgenerator.Sessions Concurrency Limit'] if 'Trafficgenerator.Sessions Concurrency Limit' in self.attributes else None

    @sessions_concurrency_limit.setter
    def sessions_concurrency_limit(self, value='1'):
        """
        The maximum number of concurrent sessions that the driver will open to the device. Default is 1 (no concurrency).
        :type value: float
        """
        self.attributes['Trafficgenerator.Sessions Concurrency Limit'] = value

    @property
    def snmp_read_community(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.SNMP Read Community'] if 'Trafficgenerator.SNMP Read Community' in self.attributes else None

    @snmp_read_community.setter
    def snmp_read_community(self, value):
        """
        The SNMP Read-Only Community String is like a password. It is sent along with each SNMP Get-Request and allows (or denies) access to device.
        :type value: string
        """
        self.attributes['Trafficgenerator.SNMP Read Community'] = value

    @property
    def snmp_write_community(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.SNMP Write Community'] if 'Trafficgenerator.SNMP Write Community' in self.attributes else None

    @snmp_write_community.setter
    def snmp_write_community(self, value):
        """
        The SNMP Write Community String is like a password. It is sent along with each SNMP Set-Request and allows (or denies) chaning MIBs values.
        :type value: string
        """
        self.attributes['Trafficgenerator.SNMP Write Community'] = value

    @property
    def snmp_v3_user(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.SNMP V3 User'] if 'Trafficgenerator.SNMP V3 User' in self.attributes else None

    @snmp_v3_user.setter
    def snmp_v3_user(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Trafficgenerator.SNMP V3 User'] = value

    @property
    def snmp_v3_password(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.SNMP V3 Password'] if 'Trafficgenerator.SNMP V3 Password' in self.attributes else None

    @snmp_v3_password.setter
    def snmp_v3_password(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: string
        """
        self.attributes['Trafficgenerator.SNMP V3 Password'] = value

    @property
    def snmp_v3_private_key(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.SNMP V3 Private Key'] if 'Trafficgenerator.SNMP V3 Private Key' in self.attributes else None

    @snmp_v3_private_key.setter
    def snmp_v3_private_key(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Trafficgenerator.SNMP V3 Private Key'] = value

    @property
    def snmp_v3_authentication_protocol(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.SNMP V3 Authentication Protocol'] if 'Trafficgenerator.SNMP V3 Authentication Protocol' in self.attributes else None

    @snmp_v3_authentication_protocol.setter
    def snmp_v3_authentication_protocol(self, value='No Authentication Protocol'):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Trafficgenerator.SNMP V3 Authentication Protocol'] = value

    @property
    def snmp_v3_privacy_protocol(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.SNMP V3 Privacy Protocol'] if 'Trafficgenerator.SNMP V3 Privacy Protocol' in self.attributes else None

    @snmp_v3_privacy_protocol.setter
    def snmp_v3_privacy_protocol(self, value='No Privacy Protocol'):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Trafficgenerator.SNMP V3 Privacy Protocol'] = value

    @property
    def snmp_version(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.SNMP Version'] if 'Trafficgenerator.SNMP Version' in self.attributes else None

    @snmp_version.setter
    def snmp_version(self, value=''):
        """
        The version of SNMP to use. Possible values are v1, v2c and v3.
        :type value: str
        """
        self.attributes['Trafficgenerator.SNMP Version'] = value

    @property
    def enable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['Trafficgenerator.Enable SNMP'] if 'Trafficgenerator.Enable SNMP' in self.attributes else None

    @enable_snmp.setter
    def enable_snmp(self, value=True):
        """
        If set to True and SNMP isn???t enabled yet in the device the Shell will automatically enable SNMP in the device when Autoload command is called. SNMP must be enabled on the device for the Autoload command to run successfully. True by default.
        :type value: bool
        """
        self.attributes['Trafficgenerator.Enable SNMP'] = value

    @property
    def disable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['Trafficgenerator.Disable SNMP'] if 'Trafficgenerator.Disable SNMP' in self.attributes else None

    @disable_snmp.setter
    def disable_snmp(self, value=False):
        """
        If set to True SNMP will be disabled automatically by the Shell after the Autoload command execution is completed. False by default.
        :type value: bool
        """
        self.attributes['Trafficgenerator.Disable SNMP'] = value

    @property
    def console_server_ip_address(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Console Server IP Address'] if 'Trafficgenerator.Console Server IP Address' in self.attributes else None

    @console_server_ip_address.setter
    def console_server_ip_address(self, value):
        """
        The IP address of the console server, in IPv4 format.
        :type value: str
        """
        self.attributes['Trafficgenerator.Console Server IP Address'] = value

    @property
    def console_user(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Console User'] if 'Trafficgenerator.Console User' in self.attributes else None

    @console_user.setter
    def console_user(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.Console User'] = value

    @property
    def console_port(self):
        """
        :rtype: float
        """
        return self.attributes['Trafficgenerator.Console Port'] if 'Trafficgenerator.Console Port' in self.attributes else None

    @console_port.setter
    def console_port(self, value):
        """
        The port on the console server, usually TCP port, which the device is associated with.
        :type value: float
        """
        self.attributes['Trafficgenerator.Console Port'] = value

    @property
    def console_password(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.Console Password'] if 'Trafficgenerator.Console Password' in self.attributes else None

    @console_password.setter
    def console_password(self, value):
        """
        
        :type value: string
        """
        self.attributes['Trafficgenerator.Console Password'] = value

    @property
    def cli_connection_type(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.CLI Connection Type'] if 'Trafficgenerator.CLI Connection Type' in self.attributes else None

    @cli_connection_type.setter
    def cli_connection_type(self, value='Auto'):
        """
        The CLI connection type that will be used by the driver. Possible values are Auto, Console, SSH, Telnet and TCP. If Auto is selected the driver will choose the available connection type automatically. Default value is Auto.
        :type value: str
        """
        self.attributes['Trafficgenerator.CLI Connection Type'] = value

    @property
    def cli_tcp_port(self):
        """
        :rtype: float
        """
        return self.attributes['Trafficgenerator.CLI TCP Port'] if 'Trafficgenerator.CLI TCP Port' in self.attributes else None

    @cli_tcp_port.setter
    def cli_tcp_port(self, value):
        """
        TCP Port to user for CLI connection. If kept empty a default CLI port will be used based on the chosen protocol, for example Telnet will use port 23.
        :type value: float
        """
        self.attributes['Trafficgenerator.CLI TCP Port'] = value

    @property
    def backup_location(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Backup Location'] if 'Trafficgenerator.Backup Location' in self.attributes else None

    @backup_location.setter
    def backup_location(self, value):
        """
        Used by the save/restore orchestration to determine where backups should be saved.
        :type value: str
        """
        self.attributes['Trafficgenerator.Backup Location'] = value

    @property
    def backup_type(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Backup Type'] if 'Trafficgenerator.Backup Type' in self.attributes else None

    @backup_type.setter
    def backup_type(self, value='File System'):
        """
        Supported protocols for saving and restoring of configuration and firmware files. Possible values are 'File System' 'FTP' and 'TFTP'. Default value is 'File System'.
        :type value: str
        """
        self.attributes['Trafficgenerator.Backup Type'] = value

    @property
    def backup_user(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.Backup User'] if 'Trafficgenerator.Backup User' in self.attributes else None

    @backup_user.setter
    def backup_user(self, value):
        """
        Username for the storage server used for saving and restoring of configuration and firmware files.
        :type value: str
        """
        self.attributes['Trafficgenerator.Backup User'] = value

    @property
    def backup_password(self):
        """
        :rtype: string
        """
        return self.attributes['Trafficgenerator.Backup Password'] if 'Trafficgenerator.Backup Password' in self.attributes else None

    @backup_password.setter
    def backup_password(self, value):
        """
        Password for the storage server used for saving and restoring of configuration and firmware files.
        :type value: string
        """
        self.attributes['Trafficgenerator.Backup Password'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def system_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.System Name'] if 'CS_GenericResource.System Name' in self.attributes else None

    @system_name.setter
    def system_name(self, value):
        """
        A unique identifier for the device, if exists in the device terminal/os.
        :type value: str
        """
        self.attributes['CS_GenericResource.System Name'] = value

    @property
    def vendor(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Vendor'] if 'CS_GenericResource.Vendor' in self.attributes else None

    @vendor.setter
    def vendor(self, value=''):
        """
        The name of the device manufacture.
        :type value: str
        """
        self.attributes['CS_GenericResource.Vendor'] = value

    @property
    def contact_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Contact Name'] if 'CS_GenericResource.Contact Name' in self.attributes else None

    @contact_name.setter
    def contact_name(self, value):
        """
        The name of a contact registered in the device.
        :type value: str
        """
        self.attributes['CS_GenericResource.Contact Name'] = value

    @property
    def location(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Location'] if 'CS_GenericResource.Location' in self.attributes else None

    @location.setter
    def location(self, value=''):
        """
        The device physical location identifier. For example Lab1/Floor2/Row5/Slot4.
        :type value: str
        """
        self.attributes['CS_GenericResource.Location'] = value

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Model'] if 'CS_GenericResource.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['CS_GenericResource.Model'] = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Model Name'] if 'CS_GenericResource.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_GenericResource.Model Name'] = value


class ResourcePort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Trafficgenerator.ResourcePort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype ResourcePort
        """
        result = ResourcePort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'ResourcePort'

    @property
    def mac_address(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.ResourcePort.MAC Address'] if 'Trafficgenerator.ResourcePort.MAC Address' in self.attributes else None

    @mac_address.setter
    def mac_address(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.ResourcePort.MAC Address'] = value

    @property
    def ipv4_address(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.ResourcePort.IPv4 Address'] if 'Trafficgenerator.ResourcePort.IPv4 Address' in self.attributes else None

    @ipv4_address.setter
    def ipv4_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.ResourcePort.IPv4 Address'] = value

    @property
    def ipv6_address(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.ResourcePort.IPv6 Address'] if 'Trafficgenerator.ResourcePort.IPv6 Address' in self.attributes else None

    @ipv6_address.setter
    def ipv6_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.ResourcePort.IPv6 Address'] = value

    @property
    def port_speed(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.ResourcePort.Port Speed'] if 'Trafficgenerator.ResourcePort.Port Speed' in self.attributes else None

    @port_speed.setter
    def port_speed(self, value):
        """
        The port speed (e.g 10Gb/s, 40Gb/s, 100Mb/s)
        :type value: str
        """
        self.attributes['Trafficgenerator.ResourcePort.Port Speed'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Port.Model Name'] if 'CS_Port.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_Port.Model Name'] = value


class GenericPowerPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Trafficgenerator.GenericPowerPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPowerPort
        """
        result = GenericPowerPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPowerPort'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.GenericPowerPort.Model'] if 'Trafficgenerator.GenericPowerPort.Model' in self.attributes else None

    @model.setter
    def model(self, value):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['Trafficgenerator.GenericPowerPort.Model'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.GenericPowerPort.Serial Number'] if 'Trafficgenerator.GenericPowerPort.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        
        :type value: str
        """
        self.attributes['Trafficgenerator.GenericPowerPort.Serial Number'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.GenericPowerPort.Version'] if 'Trafficgenerator.GenericPowerPort.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['Trafficgenerator.GenericPowerPort.Version'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['Trafficgenerator.GenericPowerPort.Port Description'] if 'Trafficgenerator.GenericPowerPort.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['Trafficgenerator.GenericPowerPort.Port Description'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_PowerPort.Model Name'] if 'CS_PowerPort.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_PowerPort.Model Name'] = value



