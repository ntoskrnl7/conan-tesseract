#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools


class TesseractConan(ConanFile):
    name = "tesseract"
    version = "3.05.01"
    description = "Tesseract Open Source OCR Engine"
    url = "http://github.com/bincrafters/conan-tesseract"
    license = "Apache-2.0"
    homepage = "https://github.com/tesseract-ocr/tesseract"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_training": [True, False]}
    default_options = "shared=False", "fPIC=True", "with_training=False"
    source_subfolder = "source_subfolder"

    requires = "leptonica/1.75.1@bincrafters/stable"

    def source(self):
        tools.get("https://github.com/tesseract-ocr/tesseract/archive/%s.tar.gz" % self.version)
        os.rename("tesseract-" + self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def config_options(self):
        if self.options.with_training:
            raise Exception("Build with training is not yet supported")

    def system_requirements(self):
        """ Temporary requirement until pkgconfig_installer is introduced """
        if tools.os_info.is_linux and tools.os_info.with_apt:
            installer = tools.SystemPackageTool()
            installer.install('pkg-config')

    def build_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions['BUILD_TRAINING_TOOLS'] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["STATIC"] = not self.options.shared

        # provide patched lept.pc
        shutil.copy(os.path.join(self.deps_cpp_info['leptonica'].rootpath, 'lib', 'pkgconfig', 'lept.pc'), 'lept.pc')
        tools.replace_prefix_in_pc_file("lept.pc", self.deps_cpp_info['leptonica'].rootpath)

        # if static leptonica used, tesseract must use Leptonica_STATIC_LIBRARIES
        # which use static dependencies like jpeg, png etc provided by lept.pc
        if not self.options['leptonica'].shared:
            tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"),
                    "target_link_libraries       (libtesseract ${Leptonica_LIBRARIES})",
                    "target_link_libraries       (libtesseract ${Leptonica_STATIC_LIBRARIES})")

        if self.version == "3.05.01":
            # upstream bug: output name is not substituted for tesseract.pc
            # fixed in master but still an issue for stable
            tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"),
                    "set_target_properties           (libtesseract PROPERTIES DEBUG_OUTPUT_NAME tesseract${VERSION_MAJOR}${VERSION_MINOR}d)",
                    "set_target_properties           (libtesseract PROPERTIES DEBUG_OUTPUT_NAME tesseract${VERSION_MAJOR}${VERSION_MINOR}d)\n"
                    "else()\n"
                    "set_target_properties           (libtesseract PROPERTIES OUTPUT_NAME tesseract)\n")

        with tools.environment_append({'PKG_CONFIG_PATH': self.build_folder}):
            cmake.configure(source_folder=self.source_subfolder)
            cmake.build()
            cmake.install()

        # Fix pc file: cmake does not fill libs.private
        if self.settings.os != 'Windows':
            libs_private = []
            libs_private.extend(['-L'+path for path in self.deps_cpp_info['leptonica'].lib_paths])
            libs_private.extend(['-l'+lib for lib in self.deps_cpp_info['leptonica'].libs])
            path = os.path.join(self.package_folder, 'lib', 'pkgconfig', 'tesseract.pc')
            tools.replace_in_file(path,
                                 'Libs.private:',
                                 'Libs.private: ' + ' '.join(libs_private))


    def build(self):
        if self.settings.compiler == "Visual Studio":
            raise Exception("Windows build not supported")
        else:
            self.build_cmake()

    def package(self):
        self.copy("LICENSE", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        # remove man pages
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'man'), ignore_errors=True)
        # remove binaries
        for ext in ['', '.exe']:
            try:
                os.remove(os.path.join(self.package_folder, 'bin', 'tesseract'+ext))
            except:
                pass


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread"])
