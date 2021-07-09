{ lib
, buildPythonPackage
, numpy
, numba
, requests
, scipy
, dataclasses-json
, shapely
, pathos
}:

buildPythonPackage {
  name = "kyzylborda";

  src = lib.cleanSourceWith {
    filter = name: type: let baseName = baseNameOf (toString name); in !lib.hasSuffix ".nix" baseName;
    src = lib.cleanSource ./.;
  };

  propagatedBuildInputs = [
    numpy
    numba
    requests
    scipy
    dataclasses-json
    shapely
    pathos
  ];
}
