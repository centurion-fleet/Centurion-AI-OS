# nix/overlays.nix — Expose pkgs.centurion-ai-os for external NixOS configs
{ inputs, ... }:
{
  flake.overlays.default = final: _: {
    centurion-ai-os = final.callPackage ./centurion-ai-os.nix {
      inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
      npm-lockfile-fix = inputs.npm-lockfile-fix.packages.${final.stdenv.hostPlatform.system}.default;
      rev = inputs.self.rev or null;
    };
  };
}
