import subprocess


def restart_systemd_service(service_name):
    try:
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        print(f"The {service_name} service has been restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while restarting {service_name} service: {e}")


def systemd_service_is_active(service_name: str) -> bool:
    try:
        cmd = f"systemctl is-active --quiet {service_name}"
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
