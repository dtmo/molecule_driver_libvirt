"""Libvirt Driver Module."""
from __future__ import annotations
import logging
import os

from typing import TYPE_CHECKING, Any

from molecule import util
from molecule.api import Driver

if TYPE_CHECKING:
    from molecule.config import Config

LOG = logging.getLogger(__name__)

class Libvirt(Driver):
    title = "Libvirt driver, user specifies VMs to create with libvirt."

    def __init__(self, config: Config) -> None:
        """Construct Libvirt.

        Args:
            config: An instance of a Molecule config.
        """
        super().__init__(config)
        self._name = "molecule_libvirt"

    @property
    def name(self) -> str:
        """Name of the driver.

        Returns:
            Name of the driver.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Driver name setter.

        Args:
            value: New name of the driver.
        """
        self._name = value

    @property
    def login_cmd_template(self) -> str:
        """Get the login command template to be populated by ``login_options`` as a string.

        Returns:
            The login command template, if any.
        """
        if "login_cmd_template" in self.options:
            return self.options["login_cmd_template"]

        if self.managed:
            connection_options = " ".join(self.ssh_connection_options)

            return (
                "ssh {address} "
                "-l {user} "
                "-p {port} "
                "-i {identity_file} "
                f"{connection_options}"
            )
        return ""

    @property
    def default_safe_files(self) -> list[str]:
        """Generate files to be preserved.

        Returns:
            List of files to be preserved.
        """
        return []

    @property
    def default_ssh_connection_options(self) -> list[str]:
        """SSH client options.

        Returns:
            List of SSH connection options.
        """
        if self.managed:
            ssh_connopts = self._get_ssh_connection_options()
            if config_connopts := self.options.get("ansible_connection_options", {}).get(
                "ansible_ssh_common_args",
            ):
                ssh_connopts.append(
                    config_connopts,
                )
            return ssh_connopts
        return []

    def login_options(self, instance_name: str) -> dict[str, str]:
        """Login options.

        Args:
            instance_name: The name of the instance to look up login options for.

        Returns:
            Dictionary of options related to logging into the instance.
        """
        if self.managed:
            d = {"instance": instance_name}

            return util.merge_dicts(d, self._get_instance_config(instance_name))
        return {"instance": instance_name}

    def ansible_connection_options(
        self,
        instance_name: str,
    ) -> dict[str, str]:
        """Ansible connection options.

        Args:
            instance_name: The name of the instance to look up Ansible connection options for.

        Returns:
            Dictionary of options related to ansible connection to the instance.
        """
        # list of tuples describing mappable instance params and default values
        instance_params = [
            ("become_pass", None),
            ("become_method", False),
            ("winrm_transport", None),
            ("winrm_cert_pem", None),
            ("winrm_cert_key_pem", None),
            ("winrm_server_cert_validation", None),
            ("shell_type", None),
            ("connection", "smart"),
        ]
        if self.managed:
            try:
                d = self._get_instance_config(instance_name)
                conn_dict = {}
                # Check if optional mappable params are in the instance config
                for i in instance_params:
                    if d.get(i[0], i[1]):
                        conn_dict["ansible_" + i[0]] = d.get(i[0], i[1])

                conn_dict["ansible_user"] = d.get("user")
                conn_dict["ansible_host"] = d.get("address")
                conn_dict["ansible_port"] = d.get("port")

                if d.get("identity_file", None):
                    conn_dict["ansible_private_key_file"] = d.get("identity_file")
                if d.get("password", None):
                    conn_dict["ansible_password"] = d.get("password")
                    # Based on testinfra documentation, ansible password must be passed via ansible_ssh_pass
                    # issue to fix this can be found https://github.com/pytest-dev/pytest-testinfra/issues/580
                    conn_dict["ansible_ssh_pass"] = d.get("password")

                conn_dict["ansible_ssh_common_args"] = " ".join(
                    self.ssh_connection_options,
                )

                return conn_dict  # noqa: TRY300

            except StopIteration:
                return {}
            except OSError:
                # Instance has yet to be provisioned , therefore the
                # instance_config is not on disk.
                return {}
        return self.options.get("ansible_connection_options", {})

    def _created(self) -> str:
        if self.managed:
            return super()._created()
        return "unknown"

    def _get_instance_config(self, instance_name: str) -> dict[str, Any]:
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(item for item in instance_config_dict if item["instance"] == instance_name)

    def sanity_checks(self) -> None:
        """Run sanity checks."""
        # Note: Not implemented yet

    def schema_file(self) -> str:
        """Return schema file path.

        Returns:
            Path to schema file.
        """
        return os.path.join(self._path, "driver.json")

    @property
    def required_collections(self) -> dict[str, str]:
        """Return collections dict containing names and versions required."""
        return {
            "ansible.posix": "1.5.4",
            "community.crypto": "2.18.0",
            "community.libvirt": "1.3.0",
        }
