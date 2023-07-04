#*****************************************************************************
#   Copyright 2004-2008 Steve Menard
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#   
#*****************************************************************************

import _jpype
import _jclass

class JPackage(object) :
    def __init__(self, name) :
        self.__name = name
        
    def __getattribute__(self, n):
        try:
            return object.__getattribute__(self, n)
        except:
            # not found ...

            # perhaps it is a class?
            subname = f"{self.__name}.{n}"
            cc = _jpype.findClass(subname)
            cc = JPackage(subname) if cc is None else _jclass._getClassFor(cc)
            self.__setattr__(n, cc, True)

            return cc
            
    def __setattr__(self, n, v, intern=False):
        if n[: len("_JPackage")] != '_JPackage' and not intern: # NOTE this shadows name mangling
            raise (RuntimeError, f"Cannot set attributes in a package{n}")
        object.__setattr__(self, n, v)
        
    def __str__(self):
        return f"<Java package {self.__name}>"
        
    def __call__(self, *arg, **kwarg):
        raise (TypeError, f"Package {self.__name} is not Callable")
