{ name, domain
, emailHost, emailPort, emailUser ? null, emailFrom
, binPackages ? [], pythonPackages ? (self: [])
, tasks ? "./tasks"
, externalKey ? null, registrationEnabled ? false
, namedScoreboards ? {}
, defaultTaskAttrs ? {}
, ... }@args:

{ lib, config, pkgs, ... }:

with lib;

let
  app = pkgs.python3.pkgs.callPackage ./. { };
  uwsgiSock = "/run/uwsgi/${name}.sock";
  myPython = pkgs.python3.withPackages (pkgs: [ app ] ++ pythonPackages pkgs);

  commonConfig = {
    "TASKS_PATH" = tasks;
  };

  boardConfig = commonConfig // {
    "TZ" = "Asia/Yekaterinburg";
    "DATABASE" = "postgresql:///${name}";
    "SECRET_KEY" = "REPLACE_BY_SECRET";
    "SMTP_HOST" = emailHost;
    "SMTP_PORT" = emailPort;
    "SMTP_LOGIN" = emailUser;
    "SMTP_PASSWORD" = if emailUser != null then "REPLACE_BY_EMAIL_PASSWORD" else null;
    "EMAIL_FROM" = emailFrom;
    "DYNAMIC_ATTACHMENTS_PATH" = "./stuff";
    "EXTERNAL_KEY_PATH" = if externalKey == null then null else "./external-key.pub";
    "REGISTRATION_ENABLED" = registrationEnabled;
    "BABEL_DEFAULT_LOCALE" = "ru";
    "NAMED_SCOREBOARDS" = namedScoreboards;
    "DEFAULT_TASK_ATTRS" = defaultTaskAttrs;
  };

  supervisorConfig = commonConfig // {
    "DAEMONS_STATE_PATH" = "./daemons-state";
    "COMMON_MOUNTS" = [ "/bin" "/usr" "/nix/store" ];
    "HTTP_REDIRECT_SOCK" = "./http.sock";
  };

in {
  imports = [ ../config-common.nix ];

  services.postgresql = {
    enable = true;
    ensureDatabases = [ name ];
    ensureUsers = [
      { name = name; ensurePermissions = { "DATABASE ${name}" = "ALL PRIVILEGES"; }; }
    ];
  };

  services.nginx = {
    enable = true;
    virtualHosts."${domain}" = {
      forceSSL = true;
      enableACME = true;
      locations = {
        "/".extraConfig = ''
          uwsgi_pass unix:${uwsgiSock};
          include ${pkgs.nginx}/conf/uwsgi_params;
        '';
        "/static".root = "${app}/${pkgs.python3.sitePackages}/kyzylborda/web";
      };
    };
    virtualHosts."~^(?<task>.*)\\.${replaceStrings ["."] ["\\."] domain}" = {
      forceSSL = true;
      useACMEHost = domain;
      locations."/" = {
        # We don't use `proxyPass` to set custom Host header.
        extraConfig = ''
          proxy_pass http://unix:/var/lib/${name}-supervisor/http.sock;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection $connection_upgrade;
          proxy_set_header Host $task;
        '';
      };
    };
  };

  security.acme.certs.${domain} = {
    webroot = mkForce null;
    extraDomainNames = [ "*.${domain}" ];
    dnsProvider = "cloudflare";
    credentialsFile = "/root/ugractf/kyzylborda-secrets/cloudflare-api-keys";
  };

  services.uwsgi = {
    enable = true;
    plugins = [ "python3" ];
    instance = {
      type = "emperor";
      vassals = {
        ${name} = config.ugractf.commonUwsgiConfig // {
          plugins = [ "python3" ];
          pythonPackages = pkgs: [ app ] ++ pythonPackages pkgs;
          env = [
            "CONFIG=/var/lib/${name}/config.json"
            "PATH=${makeBinPath ([ pkgs.nix pkgs.docker ] ++ binPackages)}"
            "NIX_PATH=${concatStringsSep ":" config.nix.nixPath}"
          ];
          socket = uwsgiSock;
          chdir = "/var/lib/${name}";
          uid = name;
          gid = "uwsgi";
          logger = "syslog:${name}";
          module = "kyzylborda.web.wsgi";
          callable = "app";
        };
      };
    };
  };

  systemd.services."prepare-${name}" = {
    wantedBy = [ "multi-user.target" ];
    before = [ "uwsgi.service" "${name}-supervisor.service" ];
    serviceConfig.Type = "oneshot";
    path = [ pkgs.openssh ];
    script = ''
      secret="$(cat ${toString ../kyzylborda-secrets/secret.txt})"
      ${lib.optionalString (emailUser != null) ''
        email_password="$(cat ${toString ../kyzylborda-secrets/email-password.txt})"
      ''}
      sed \
        -e "s,REPLACE_BY_SECRET,$secret," \
        ${lib.optionalString (emailUser != null) ''-e "s,REPLACE_BY_EMAIL_PASSWORD,$email_password,"''} \
        ${pkgs.writeText "config.json" (builtins.toJSON boardConfig)} > /var/lib/${name}/config.json
      ${optionalString (externalKey != null) ''
        cp ${toString externalKey} /var/lib/${name}/external-key.pub
      ''}
    '';
  };

  systemd.services."${name}-supervisor" = {
    wantedBy = [ "multi-user.target" ];
    # Mainline is used for `error_log stderr`.
    path = [ myPython pkgs.nginxMainline pkgs.bubblewrap pkgs.nix pkgs.docker ] ++ binPackages;
    environment."NIX_PATH" = concatStringsSep ":" config.nix.nixPath;
    serviceConfig = {
      ExecStart = "${myPython}/bin/python -m kyzylborda.supervisor ${pkgs.writeText "config.json" (builtins.toJSON supervisorConfig)}";
      User = "${name}-supervisor";
      Group = "nobody";
      StateDirectory = "${name}-supervisor";
      WorkingDirectory = "/var/lib/${name}-supervisor";
    };
  };

  users.extraUsers.${name} = {
    group = "uwsgi";
    home = "/var/lib/${name}";
    extraGroups = [ "docker" ];
  };

  users.extraUsers."${name}-supervisor" = {
    group = "uwsgi";
    extraGroups = [ "docker" ];
  };

  system.activationScripts.mkBoardDir = ''
    mkdir -p /var/lib/${name}
    chown ${name}:uwsgi /var/lib/${name}
    chmod 700 /var/lib/${name}
  '';
}
