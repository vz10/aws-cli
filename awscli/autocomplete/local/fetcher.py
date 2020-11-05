# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


class CliDriverFetcher:
    SERVICE_MAPPER = {'s3api': 's3'}

    def __init__(self, cli_driver):
        self._cli_driver = cli_driver

    def _get_argument(self, lineage, current_command, arg_name):
        subcommand_table = self._cli_driver.subcommand_table
        for arg in lineage[1:]:
            subcommand = subcommand_table[arg]
            subcommand_table = subcommand.subcommand_table
        command = subcommand_table.get(current_command)
        if command:
            return command.arg_table.get(arg_name)

    def get_operation_model(self, lineage, current_command, operation):
        if current_command and len(lineage) > 1:
            try:
                service_name = self.SERVICE_MAPPER.get(lineage[1], lineage[1])
                service_model = self._cli_driver.session.get_service_model(
                    service_name)
                operation = ''.join([part.capitalize()
                                     for part in current_command.split('-')])
                return service_model.operation_model(operation)
            except Exception:
                return

    def get_argument_model(self, lineage, current_command, arg_name):
        return getattr(self._get_argument(
            lineage, current_command, arg_name), 'argument_model', None)

    def get_argument_documentation(self, lineage, current_command, arg_name):
        return getattr(self._get_argument(
            lineage, current_command, arg_name), 'documentation', '')

    def get_global_arg_documentation(self, arg_name):
        return self._cli_driver.arg_table[arg_name].documentation

    def get_global_arg_choices(self, arg_name):
        if arg_name in self._cli_driver.arg_table:
            return self._cli_driver.arg_table[arg_name].choices
