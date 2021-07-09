{
  inputs = {
    nixpkgs.url =  "github:abbradar/nixpkgs/ugractf";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
           pkgs = import nixpkgs { inherit system; };
           pkg = import ./shell.nix { inherit pkgs; };
        in {
          devShell = pkgs.lib.overrideDerivation pkg (drv: {
            NIX_PATH = "nixpkgs=${nixpkgs}";
          });
          defaultPackage = pkg;
        }
      );
}
