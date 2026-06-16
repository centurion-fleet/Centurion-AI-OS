# nix/packages.nix — Centurion AI OS package built with uv2nix
{ inputs, ... }:
{
  perSystem =
    { pkgs, inputs', ... }:
    let
      centurionAgent = pkgs.callPackage ./centurion-ai-os.nix {
        inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
        npm-lockfile-fix = inputs'.npm-lockfile-fix.packages.default;
        # Only embed clean revs — dirtyRev doesn't represent any upstream
        # commit, so comparing it would always claim "update available".
        rev = inputs.self.rev or null;
      };
    in
    {
      packages = {
        default = centurionAgent;
        tui = centurionAgent.centurionTui;
        web = centurionAgent.centurionWeb;

        fix-lockfiles = centurionAgent.centurionNpmLib.mkFixLockfiles {
          packages = [ centurionAgent.centurionTui centurionAgent.centurionWeb ];
        };
      };
    };
}
