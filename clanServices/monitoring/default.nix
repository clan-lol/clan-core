{
  _class = "clan.service";
  manifest = {
    name = "monitoring";
    description = "Monitoring stack gathering metrics and logs with a small resource footprint.";
  };

  roles = {
    client = {
      description = "Monitoring clients send their metrics and logs to the monitoring server.";
    };

    server = {
      description = "The monitoring server that stores metrics and logs. Provides optional dashboards and alerting.";
    };
  };
}
