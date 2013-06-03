from distutils.core import setup, Extension
import distutils.core
import distutils.command.build_ext

import pybindgen
from pybindgen import FileCodeSink
from pybindgen.gccxmlparser import ModuleParser

def dynamixel_gen():
    module_parser = ModuleParser("dynamixel","::")
    module = module_parser.parse(["DXL_SDK_LINUX_v1_01/include/dynamixel.h"])
    #pybindgen.write_preamble(FileCodeSink(sys.stdout))
    module.add_include('"dynamixel.h"')
    module.generate(FileCodeSink(open("dynamixel.c","w+")))

class build_bindings(distutils.command.build_ext.build_ext):
    def run(self):
        dynamixel_gen()
        
        distutils.command.build_ext.build_ext.run(self)

dynamixel_mod = Extension('dynamixel',
                    sources = ['DXL_SDK_LINUX_v1_01/src/dxl_hal.c',
                        'DXL_SDK_LINUX_v1_01/src/dynamixel.c',
                        'dynamixel.c'],
                    include_dirs = ['DXL_SDK_LINUX_v1_01/src/','DXL_SDK_LINUX_v1_01/include'])

setup (name = 'PyUSB2AX',
        version = '1.0',
        description = 'Python binding for controlling USB2AX',
        ext_modules = [dynamixel_mod],
        cmdclass = {"build_ext":build_bindings} )
