import os
import logging
from typing import Tuple, Callable, Any

import dukpy
from dukpy import JSInterpreter
from dukpy.module_loader import JSModuleLoader

from tools.pxt.project import Project

dirname = os.path.dirname(__file__)


class Simulator:
    def __init__(self, project: Project) -> None:
        self.__project = project
        # Cached transpiled code by file name
        self.__transpilation_cache: Dict[str, str] = {}

        self.__interpreter = JSInterpreter()
        # Monkey patch the load function to accept files from memory
        self.__create_load_patch(self.__interpreter._loader)
        self.__interpreter._init_require()

        self.__modules: Dict[str, str] = {}
        self.__load_default_modules()

        log = logging.getLogger('dukpy.interpreter')
        log.level = logging.DEBUG

    @property
    def project(self) -> Project:
        """The project."""
        return self.__project

    def __load_default_modules(self) -> None:
        with open(os.path.join(dirname, "./require/system.js"), "r") as file:
            self.__modules["__/require/system"] = file.read()
        with open(os.path.join(dirname, "./require/promise.js"), "r") as file:
            self.__modules["__/require/promise"] = file.read()
        self.__modules["main"] = self.__transpile("main.ts")

    def __create_load_patch(self, loader: JSModuleLoader) -> Callable[..., Any]:
        def load_patch(module_name: str) -> Tuple[str, str]:
            """Monkey patch for returning the source code for a given module."""
            print("load", module_name)
            if module_name in self.__modules:
                return (module_name, self.__modules[module_name])
            return (None, None)
        loader.load = load_patch

    def __transpile(self, filename: str) -> str:
        """Transpile a TypeScript source file in the project."""
        if filename in self.__transpilation_cache:
            return self.__transpilation_cache[filename]

        self.__transpilation_cache[filename] = dukpy.typescript_compile(self.__project.file_by_name(filename))
        print(self.__transpilation_cache[filename])
        return self.__transpilation_cache[filename]

    def run(self) -> None:
        self.__interpreter.evaljs(
            """
            // Define a NodeJS-like "global" object
            // See: https://wiki.duktape.org/howtoglobalobjectreference
            if (typeof global === 'undefined') {
                (function () {
                    var global = new Function('return this;')();
                    Object.defineProperty(global, 'global', {
                        value: global,
                        writable: true,
                        enumerable: false,
                        configurable: true
                    });
                })();
            }

            // Require a promise polyfill
            global.Promise = require('./__/require/promise');

            // Include System.js to resolve TypeScript imports at runtime
            // This path could be anything, but it should never be able to collide
            // with anything used by MakeCode or the user
            require('./__/require/system');
            """
        )

        self.__interpreter.evaljs(
            """
            var brick = {
                setStatusLight: function() {},
                showMood: function() {}
            };

            var motors = {
                largeA: {
                    run: function() {}
                }
            }

            try {
                require('./main');
                System.import('./main').then(function() {
                  console.log("Complete");
                }).catch(function(error) {
                  console.log("Unable to load main")
                  console.error(error);
                });
            } catch (error) {
                console.log("Failed simulation");
                console.error(error.stack);
            }
            """
        )
