{ pkgs ? import <nixpkgs> {} }:

let
  py = pkgs.python3;
  pkg = py.pkgs.callPackage ./. { };
in pkg.overrideAttrs (self: {
  nativeBuildInputs = [ py.pkgs.jupyter ];
})
