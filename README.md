# molecule_driver_libvirt

A driver for
[Ansible Molecule](https://ansible.readthedocs.io/projects/molecule/) with
[libvirt](https://libvirt.org/) and [QEMU](https://www.qemu.org/).

## Required Packages

* [libvirt](https://libvirt.org/)
* [libvirt-python](https://pypi.org/project/libvirt-python/)
* [QEMU](https://www.qemu.org/)
* [xorriso](https://www.gnu.org/software/xorriso/)

### Ubuntu 24.04 Set Up

```bash
sudo apt install -y \
    git \
    libvirt-clients \
    libvirt-dev \
    python3-libvirt \
    python3-pip \
    python3-venv \
    virt-manager \
    xorriso

python3.12 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/dtmo/molecule_driver_libvirt.git ansible-lint
molecule --version
```

### Fedora 42 Set Up

```bash
sudo dnf install -y \
    gcc \
    git \
    libvirt-client-qemu \
    libvirt-devel \
    python3-devel \
    python3-libvirt \
    python3-pip \
    python3-venv \
    virt-manager \
    xorriso
```

## Compatible VM Images

This driver has some specific requirements for VM images that it uses.

* The guest OS must have [Cloud-init](https://cloud-init.io/) installed with the
  [NoCloud Datasource](https://cloudinit.readthedocs.io/en/latest/reference/datasources/nocloud.html)
  enabled. xorriso is used to create an ISO image containing Cloud-init
  `meta-data`, `user-data` and `vendor-data` files, which is then mounted on the
  VM.
* The guest OS must have the
  [QEMU Guest Agent](https://wiki.qemu.org/Features/GuestAgent) installed. The
  driver uses Guest Agent commands to determine the guest OS network
  configuration, and to determine when Cloud-init has completed initialization.
* The guest OS must be running an SSH server.
* The image is configured based on BIOS.
* The image must be configured so that first boot initialization is performed.
  For Linux machines this may mean setting systemd files appropriately for
  [First Boot Semantics](https://www.freedesktop.org/software/systemd/man/latest/machine-id.html#First%20Boot%20Semantics). For a Windows guest this would be having
  performed a Sysprep generalize. Similarly, Cloud-init must have been cleaned
  so that it performs initialization.

  See also:
  <https://www.qemu.org/docs/master/system/vm-templating.html#security-alert>

Example images that meet the above criteria may be produced with the Packer
configurations found at:

* <https://github.com/dtmo/molecule_rocky_9>
* <https://github.com/dtmo/molecule_ubuntu_2404>.

## Configuration

### Libvirt connection URI

The `molecule_libvirt` driver supports an option to specify the `libvirt_uri`,
which will override the connection URI used by libvirt connections created by
the Molecule driver from the default value of: `qemu:///system`.

See: <https://libvirt.org/uri.html>

### Platform defaults

The driver also supports specifying `defaults` which can take the following:

* `disk_file_path`: (required) The path to the QCOW2 disk file to use as the
  backing file for the VM disk.
* `os_id`: (required) The [libosinfo](https://libosinfo.org/) OS ID of the guest
  operating system. The supported values are available in the
  [osinfo-db OS data source code](https://gitlab.com/libosinfo/osinfo-db/-/tree/main/data/os?ref_type=heads).
  Common values include:
  * [CentOS Stream 9](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/centos.org/centos-stream-9.xml.in?ref_type=heads#L4)
    : `http://centos.org/centos-stream/9`
  * [Debian 9](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/debian.org/debian-9.xml.in?ref_type=heads#L4)
    : `http://debian.org/debian/9`
  * [Fedora Linux 40](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/fedoraproject.org/fedora-40.xml.in?ref_type=heads)
    : `http://fedoraproject.org/fedora/40`
  * [Red Hat Enterprise Linux 9.5](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/redhat.com/rhel-9.5.xml.in?ref_type=heads#L4)
    : `http://redhat.com/rhel/9.5`
  * [Rocky Linux 9](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/rockylinux.org/rocky-9.xml.in?ref_type=heads#L4)
    : `http://rockylinux.org/rocky/9`
  * [Ubuntu 24.04 LTS](https://gitlab.com/libosinfo/osinfo-db/-/blob/main/data/os/ubuntu.com/ubuntu-24.04.xml.in?ref_type=heads#L5)
    : `http://ubuntu.com/ubuntu/24.04`
* `ssh_user`: (required) The name of the user account to use for SSH. This is
  set as the Cloud-init default user name.
* `disk_size`: (optional) The size of the disk. If not set then the size
  specified in the QCOW2 backing file is used. Optional suffixes:
  * b (bytes).
  * k or K (kilobyte, 1024b)
  * M (megabyte, 1024k)
  * G (gigabyte, 1024M)
  * T (terabyte, 1024G)
* `ram_mib`: (required) The amount of RAM in mebibytes.
* `vcpus`: (required) The number of vCPUs.
* `user_data`: (optional) Cloud-init user data to provide to the VM guest OS.

### Platform configuration

Each platform has the following configuration properties:

* `name`: (required) The name of the host to create. This is set as the guest
  hostname, and combined with the Molecule state `run_uuid` value to create a
  unique VM name.
* All values supported as driver platform defaults. When a value is specified as
  a platform value it will override a default specified in the driver.

## Example `molecule.yml`

```yaml
driver:
  name: molecule_libvirt
  defaults:
    disk_file_path: "{{ ubuntu_2404_qcow2_image_path }}"
    os_id: http://ubuntu.com/ubuntu/24.04
    ssh_user: ansible
    disk_size: 50G
    ram_mib: 4096
    vcpus: 2
platforms:
  - name: instance
  - name: big_instance
    disk_size: 500G
    ram_mib: 16384
    vcpus: 16

```
