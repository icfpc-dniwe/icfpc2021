{ lib
, buildPythonPackage
, numpy
, requests
}:

buildPythonPackage {
  name = "kyzylborda";

  src = lib.cleanSourceWith {
    filter = name: type: let baseName = baseNameOf (toString name); in !lib.hasSuffix ".nix" baseName;
    src = lib.cleanSource ./.;
  };

  propagatedBuildInputs = [
    numpy
    requests
  ];
}
