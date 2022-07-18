# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj — Nix package file
# :Created:   dom 17 lug 2022, 11:06:06
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2022 Alberto Berti
#

{
  description = "JavaScripthon: a Python 3 to ES6 JavaScript translator";

  inputs = {
    dukpy = {
      url = "github:amol-/dukpy/0.2.3";
      flake = false;
    };
    flake-utils.url = "github:numtide/flake-utils";
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      # Use the same nixpkgs
      inputs.nixpkgs.follows = "nixpkgs";
    };
    meta = {
      url = "github:srossross/Meta/0.4.1";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, dukpy, flake-utils, gitignore, meta}:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        inherit (pkgs.lib) genAttrs recursiveUpdate;
        inherit (builtins) elemAt filter getAttr;
        inherit (gitignore.lib) gitignoreSource;
        pyVersions = ["python37" "python38" "python39" "python310"];
        /* Find the Python version associated with `pkgs.python3`*/
        findDefaultPyVersion =
          let
            python3 = getAttr "python3" pkgs;
            defaultPy = filter (pyv: (getAttr pyv pkgs) == python3) pyVersions;
          in elemAt defaultPy 0;
        defPyVersion = findDefaultPyVersion;
        /*
           Make a Python application out of a Python version string and some
           package details.
        */
        mkPyApp = pyVersion: details:
            let
              py = getAttr pyVersion pkgs;
            in py.pkgs.buildPythonApplication (details py pyVersion);
        /*
           Make a Python package out of a Python version string and some
           package details.
        */
        mkPyPkg = pyVersion: details:
            let
              py = getAttr pyVersion pkgs;
            in py.pkgs.buildPythonPackage (details py pyVersion);
        /*
          Make an attr containing multiple packages
        */
        mkMultiPyPkg = details:
          let
            multiPkgs = genAttrs pyVersions (pyv: mkPyPkg pyv details);
          in multiPkgs // ( rec {
            default = python3;
            python3 = getAttr defPyVersion multiPkgs;
          });
        dukpyPkg = python: pyVersion: {
          checkInputs = with python.pkgs; [
            pytest
            pytest-cov
            mock
            webassets
          ];
          checkPhase = "pytest --ignore=tests/test_installer.py";
          dontUseSetuptoolsShellHook = 1;
          pname = "dukpy";
          version = "0.2.3";
          src = dukpy;
        };
        dukpyPkgs = mkMultiPyPkg dukpyPkg;
        metaPkg = python: pyVersion: {
          doCheck = false;
          pname = "meta";
          version = "0.4.1";
          src = meta;
        };
        metaPkgs = mkMultiPyPkg metaPkg;
        pjPkg = python: pyVersion: {
          checkInputs = with python.pkgs; [
            pytest
            pytest-cov
          ];
          checkPhase = "pytest";
          pname = "javascripthon";
          propagatedBuildInputs = [
            (getAttr pyVersion dukpyPkgs)
            (getAttr pyVersion metaPkgs)
          ];
          version = builtins.readFile ./version.txt;
          src = gitignoreSource ./.;
          meta = {
            homepage = "https://github.com/azazel75/metapensiero.pj";
            description = "JavaScripthon: a Python 3 to ES6 JavaScript translator";
            license = pkgs.lib.licenses.gpl3;
            mainProgram = "pj";
          };
        };
        pjPkgs = mkMultiPyPkg pjPkg;
      in {
        apps = rec {
          default = javascripthon;
          javascripthon = {
            type = "app";
            program = "${self.outputs.packages."${system}".app}/bin/pj";
          };
          pj = javascripthon;
        };
        packages = pjPkgs // {
          all = pkgs.buildEnv {
            name = "allpjs";
            paths = map (pyv: pjPkgs."${pyv}") pyVersions;
            pathsToLink = [ "/lib" ];
          };
          app = mkPyApp defPyVersion pjPkg;
        };
        checks.default = self.outputs.packages."${system}".all;
      });
}
