#!/bin/bash

set -e

INSTALL_DIR="/home/$USER/.s3sync"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mkdir -p $INSTALL_DIR

install_python_package() {
    # Given a path to a python package and a path to target directory, spin up
    # venv, install requirements and install the "built" package into the target dir.

    local package_dir="$1"
    local install_dir="$2"

    pushd "${package_dir}" &> /dev/null || return 1

    print "info" "Spinning up venv..." 1
    python3 -m venv .venv > /dev/null
    print "inline-ok" "Spinning up venv..." 1

    # Activate the virtual environment
    source ".venv/bin/activate"

    print "info" "Installing requirements..." 1
    pip3 install -r requirements.txt | sed 's/^/       /'
    print "inline-ok" "Installing requirements..." 1

    print "info" "Installing the python3 module..." 1
    pip3 install -e . > /dev/null
    print "inline-ok" "Installing the python3 module..." 1

    # Install the .venv directory in target directory.
    rm -rf "$install_dir"; mkdir -p "$install_dir"
    mv "$package_dir"/.venv/* "$install_dir"

    popd &> /dev/null || return 1
}

install_bins() {
    local bins_dir="$1"
    
    for bin_file in "${bins_dir}"/*; do
        if [ -f "$bin_file" ]; then
            bin_name=$(basename "${bin_file}")
            print "info" "Installing ${bin_name}..." 1
            sudo install -T -m 0755 "${bin_file}" "/usr/bin/${bin_name}"
            print "inline-ok" "Installing ${bin_name}..." 1
        fi
    done
}


install_systemd_services() {
    # Given a path to a directory, install all .service files to /etc/systemd/system
    local services_dir="$1"
    
    for service_file in "${services_dir}"/*.service; do
        if [ -f "$service_file" ]; then
            service_name=$(basename "${service_file}")
            print "info" "Installing ${service_name}..." 1
            sudo install -T -m 0644 "${service_file}" "/etc/systemd/system/${service_name}"
            sudo sed -i 's/insert_target_user/'"$USER"'/g' "/etc/systemd/system/${service_name}"
            sudo systemctl enable "${service_name}"
            sudo systemctl restart "${service_name}"
            print "inline-ok" "Installing ${service_name}..." 1
        fi
    done

    sudo systemctl daemon-reload
}

print() {
    local type="$1"
    local msg="$2"
    local indent="$3"
    
    if [[ $indent == 1 ]]; then
        indent="   "
    elif [[ $indent == 2 ]]; then
        indent="      "
    else 
        indent=""
    fi

    local insert=""
    if [[ $type == "ok" || $type == "inline-ok" ]]; then
        insert="[${COL_LIGHT_GREEN}✓${COL_NC}]"
    elif [[ $type == "error" ]]; then
        insert="[${COL_LIGHT_RED}✗${COL_NC}]"
    elif [[ $type == "info" ]]; then
        insert="[i]"
    elif [[ $type == "continued" ]]; then
        insert="   "
    fi
    
    if [[ ! "$type" == *"inline"* ]]; then
        printf "${indent}${insert} ${msg}\n"
    else
        printf "\\r\\033[K${indent}${insert} ${msg}\n"
    fi 
}

main() {
    print "info" "Installing python3 package..."
    install_python_package "$SCRIPT_DIR" "$INSTALL_DIR"
    print "ok" "Done"

    print "info" "Installing binaries..."
    install_bins "$SCRIPT_DIR/bin"
    print "ok" "Done"
    
    print "info" "Installing systemd services..."
    install_systemd_services "$SCRIPT_DIR/systemd"
    print "ok" "Done"

    printf "\n"
    printf "Remmber to toss your aws credentials into '~/.s3sync.aws/credentials'."
    printf "\n"
}

main "$@"
