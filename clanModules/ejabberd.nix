{ config
, ...
}: {
  services.ejabberd = {
    enable = true;
    configFile = "/etc/ejabberd.yml";
  };

  environment.etc."ejabberd.yml" = {
    user = "ejabberd";
    mode = "0600";
    text = ''
      loglevel: 4

      default_db: sql
      new_sql_schema: true
      sql_type: sqlite
      sql_database: "/var/lib/ejabberd/db.sqlite"

      hosts:
      - ${config.clanCore.machineName}.local

      listen:
      -
        port: 5222
        ip: "::1"
        module: ejabberd_c2s
        max_stanza_size: 262144
        shaper: c2s_shaper
        access: c2s
        starttls_required: false
      -
        port: 5269
        ip: "::"
        module: ejabberd_s2s_in
        max_stanza_size: 524288

      auth_method: [anonymous]
      anonymous_protocol: login_anon
      acl:
        local:
          user_regexp: ""
        loopback:
          ip:
            - 127.0.0.0/8
            - ::1/128
      access_rules:
        local:
          allow: local
        c2s:
          deny: blocked
          allow: all
        s2s:
          - allow
        announce:
          allow: admin
        configure:
          allow: admin
        muc_create:
          allow: all
        pubsub_createnode:
          allow: local
        trusted_network:
          allow: loopback
      api_permissions:
        "console commands":
          from:
            - ejabberd_ctl
          who: all
          what: "*"
        "admin access":
          who:
            access:
              allow:
                acl: loopback
                acl: admin
            oauth:
              scope: "ejabberd:admin"
              access:
                allow:
                  acl: loopback
                  acl: admin
          what:
            - "*"
            - "!stop"
            - "!start"
        "public commands":
          who:
            ip: 127.0.0.1/8
          what:
            - status
            - connected_users_number
      shaper:
        normal: 1000
        fast: 50000

      shaper_rules:
        max_user_sessions: 10
        max_user_offline_messages:
          5000: admin
          100: all
        c2s_shaper:
          none: admin
          normal: all
        s2s_shaper: fast
      modules:
        mod_adhoc: {}
        mod_admin_extra: {}
        mod_announce:
          access: announce
        mod_avatar: {}
        mod_blocking: {}
        mod_bosh: {}
        mod_caps: {}
        mod_carboncopy: {}
        mod_client_state: {}
        mod_configure: {}
        mod_disco: {}
        mod_fail2ban: {}
        mod_http_api: {}
        mod_http_upload:
          put_url: https://@HOST@:5443/upload
        mod_last: {}
        mod_mam:
          ## Mnesia is limited to 2GB, better to use an SQL backend
          ## For small servers SQLite is a good fit and is very easy
          ## to configure. Uncomment this when you have SQL configured:
          ## db_type: sql
          assume_mam_usage: true
          default: always
        mod_mqtt:
          access_publish:
            "homeassistant/#":
              - allow: hass_publisher
              - deny
            "#":
              - deny
          access_subscribe:
            "homeassistant/#":
              - allow: hass_subscriber
              - deny
            "#":
              - deny
        mod_muc:
          host: "muc.@HOST@"
          access:
            - allow
          access_admin:
            - allow: admin
          access_create: muc_create
          access_persistent: muc_create
          access_mam:
            - allow
          default_room_options:
            mam: true
        mod_muc_admin: {}
        mod_offline:
          access_max_user_messages: max_user_offline_messages
        mod_ping: {}
        mod_privacy: {}
        mod_private: {}
        mod_proxy65:
          access: local
          max_connections: 5
        mod_pubsub:
          access_createnode: pubsub_createnode
          plugins:
            - flat
            - pep
          force_node_config:
            ## Avoid buggy clients to make their bookmarks public
            storage:bookmarks:
              access_model: whitelist
        mod_push: {}
        mod_push_keepalive: {}
        mod_register:
          ## Only accept registration requests from the "trusted"
          ## network (see access_rules section above).
          ## Think twice before enabling registration from any
          ## address. See the Jabber SPAM Manifesto for details:
          ## https://github.com/ge0rg/jabber-spam-fighting-manifesto
          ip_access: trusted_network
        mod_roster:
          versioning: true
        mod_s2s_dialback: {}
        mod_shared_roster: {}
        mod_stream_mgmt:
          resend_on_timeout: if_offline
        mod_vcard: {}
        mod_vcard_xupdate: {}
        mod_version:
          show_os: false
    '';
  };

  networking.firewall.allowedTCPPorts = [
    5269 # xmpp-server
  ];
}
