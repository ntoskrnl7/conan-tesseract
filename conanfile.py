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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    source_subfolder = "source_subfolder"

    requires = "leptonica/1.75.1@bincrafters/stable"

    def source(self):
        tools.get("https://github.com/tesseract-ocr/tesseract/archive/%s.tar.gz" % self.version)
        os.rename("tesseract-" + self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions['BUILD_TRAINING_TOOLS'] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["STATIC"] = not self.options.shared
        # it's required to set this variable.
        # otherwise tesseract uses pkg-config which cannot find static leptonica
        cmake.definitions['Leptonica_DIR'] = self.deps_cpp_info['leptonica'].rootpath

        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

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
