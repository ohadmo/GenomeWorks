#!/usr/bin/env python3

#
# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import argparse
import os.path
import os
import subprocess


def get_relative_path(sub_folder_name):
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        sub_folder_name
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description='build & install Clara Genomics Analysis SDK.')
    parser.add_argument('--build_output_folder',
                        required=False,
                        default=get_relative_path("cga_build"),
                        help="Choose an output folder for building")
    parser.add_argument('--develop',
                        required=False,
                        action='store_true',
                        help="CInstall using pip editble mode")
    return parser.parse_args()


class CMakeWrapper:
    """Class to encapsulate building a CMake project."""

    def __init__(self,
                 cmake_root_dir,
                 cmake_build_path="cmake_build",
                 cga_install_dir="cmake_build/install",
                 cmake_extra_args=""):
        """
        Class constructor.

        Args:
            cmake_root_dir : Root directory of CMake project
            cmake_build_path : cmake build output folder
            cga_install_dir: Clara Genomics Analysis installation directory
            cmake_extra_args : Extra string arguments to be passed to CMake during setup
        """
        self.cmake_root_dir = os.path.abspath(cmake_root_dir)
        self.build_path = os.path.abspath(cmake_build_path)
        self.cga_install_dir = os.path.abspath(cga_install_dir)
        self.cmake_extra_args = cmake_extra_args
        self.cuda_toolkit_root_dir = os.environ.get("CUDA_TOOLKIT_ROOT_DIR")

    def run_cmake_cmd(self):
        cmake_args = ['-DCMAKE_INSTALL_PREFIX=' + self.cga_install_dir,
                      '-DCMAKE_BUILD_TYPE=' + 'Release',
                      '-DCMAKE_INSTALL_RPATH=' + os.path.join(self.cga_install_dir, "lib")]
        cmake_args += [self.cmake_extra_args] if self.cmake_extra_args else []

        if self.cuda_toolkit_root_dir:
            cmake_args += ["-DCUDA_TOOLKIT_ROOT_DIR=%s" % self.cuda_toolkit_root_dir]

        if not os.path.exists(self.build_path):
            os.makedirs(self.build_path)

        subprocess.check_call(['cmake', self.cmake_root_dir] + cmake_args, cwd=self.build_path)

    def run_build_cmd(self):
        build_args = ['--', '-j16', 'install']
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_path)

    def build(self):
        self.run_cmake_cmd()
        self.run_build_cmd()


def setup_python_binding(is_develop_mode, pycga_dir, cga_install_dir):
    subprocess.check_call(['pip', 'install'] + (['-e'] if is_develop_mode else []) + ["."],
                          env={
                              **os.environ,
                              'PYCGA_DIR': pycga_dir,
                              'CGA_INSTALL_DIR': cga_install_dir
                          },
                          cwd=pycga_dir)


if __name__ == "__main__":

    args = parse_arguments()
    cga_build_folder = os.path.realpath(args.build_output_folder)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    cga_installation_directory = os.path.join(cga_build_folder, "install")
    # Build & install Clara Genomics Analysis SDK
    cmake_proj = CMakeWrapper(cmake_root_dir=os.path.dirname(current_dir),
                              cmake_build_path=cga_build_folder,
                              cga_install_dir=cga_installation_directory,
                              cmake_extra_args="-Dcga_build_shared=ON")
    cmake_proj.build()
    # Setup pyclaragenomics
    setup_python_binding(is_develop_mode=args.develop,
                         pycga_dir=current_dir,
                         cga_install_dir=cga_installation_directory)
    print("pyclaragenomics was successfully setup in {} mode!"
          .format("development" if args.develop else "installation"))