{ lib
, buildPythonPackage
, numpy
, numba
, requests
, dataclasses-json
, shapely
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
    dataclasses-json
    shapely
  ];
}
