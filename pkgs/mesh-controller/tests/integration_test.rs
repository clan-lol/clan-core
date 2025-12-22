//! Integration test for mesh controller with JSON whitelist.

use std::fs;
use std::io::{BufRead, BufReader};
use std::net::{Ipv6Addr, TcpStream};
use std::os::unix::process::CommandExt;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

use tempfile::TempDir;

const MESH_BIN: &str = "MESH_BIN";

fn mesh_binary() -> String {
    std::env::var(MESH_BIN).expect("MESH_BIN environment variable must be set")
}

/// Compute deterministic IPv6 from network and node IDs
fn compute_mesh_ip(network_id: u64, node_id: u64) -> Ipv6Addr {
    Ipv6Addr::from([
        0xFD,
        (network_id >> 56) as u8,
        (network_id >> 48) as u8,
        (network_id >> 40) as u8,
        (network_id >> 32) as u8,
        (network_id >> 24) as u8,
        (network_id >> 16) as u8,
        (network_id >> 8) as u8,
        network_id as u8,
        0x99,
        0x93,
        (node_id >> 32) as u8,
        (node_id >> 24) as u8,
        (node_id >> 16) as u8,
        (node_id >> 8) as u8,
        node_id as u8,
    ])
}

/// Poll until condition is true or timeout
fn wait_until(timeout: Duration, mut condition: impl FnMut() -> bool) -> bool {
    let start = Instant::now();
    while start.elapsed() < timeout {
        if condition() {
            return true;
        }
        std::thread::sleep(Duration::from_millis(500));
    }
    false
}

/// A running mesh node
struct MeshNode {
    process: Child,
    home: TempDir,
    port: u16,
}

impl MeshNode {
    fn spawn(label: &str, identity_secret: &str, config_files: &[(&str, String)]) -> Self {
        let port = TcpStream::connect("127.0.0.1:0")
            .err()
            .map(|_| std::net::TcpListener::bind("127.0.0.1:0").unwrap().local_addr().unwrap().port())
            .unwrap();
        let home = TempDir::new().unwrap();

        // Write identity
        fs::write(home.path().join("identity.secret"), identity_secret).unwrap();

        // Write config files
        for (name, content) in config_files {
            fs::write(home.path().join(name), content).unwrap();
        }

        // Copy MacEthernetTapAgent on macOS
        #[cfg(target_os = "macos")]
        {
            let agent = std::path::Path::new(&mesh_binary()).parent().unwrap().join("MacEthernetTapAgent");
            if agent.exists() {
                fs::copy(&agent, home.path().join("MacEthernetTapAgent")).unwrap();
            }
        }

        let mut cmd = Command::new("sudo");
        cmd.args(["-E", &mesh_binary(), &format!("-p{}", port)])
            .arg(home.path())
            .env("ZT_HOME", home.path())
            .stdin(Stdio::null())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        // New process group for cleanup
        unsafe {
            cmd.pre_exec(|| {
                libc::setpgid(0, 0);
                Ok(())
            });
        }

        let mut process = cmd.spawn().expect("Failed to spawn node");

        // Drain stderr
        let stderr = process.stderr.take().unwrap();
        let label = label.to_string();
        std::thread::spawn(move || {
            for line in BufReader::new(stderr).lines().map_while(Result::ok) {
                eprintln!("[{}] {}", label, line);
            }
        });

        assert!(
            wait_until(Duration::from_secs(10), || TcpStream::connect(("127.0.0.1", port)).is_ok()),
            "Node failed to start on port {}", port
        );

        Self { process, home, port }
    }

    fn cli(&self, args: &[&str]) -> String {
        let output = Command::new("sudo")
            .args([&mesh_binary(), "-q", &format!("-D{}", self.home.path().display()), &format!("-p{}", self.port)])
            .args(args)
            .output()
            .expect("Failed to run mesh-cli");
        String::from_utf8_lossy(&output.stdout).into_owned()
    }

    fn cli_json(&self, args: &[&str]) -> Option<serde_json::Value> {
        let mut full_args = args.to_vec();
        full_args.push("-j");
        serde_json::from_str(&self.cli(&full_args)).ok()
    }

    fn network_status(&self, network_id: &str) -> Option<(String, Vec<String>)> {
        let networks = self.cli_json(&["listnetworks"])?;
        let net = networks.as_array()?.iter().find(|n| n["nwid"].as_str() == Some(network_id))?;
        let status = net["status"].as_str()?.to_string();
        let ips = net["assignedAddresses"]
            .as_array()?
            .iter()
            .filter_map(|v| v.as_str())
            .map(|s| s.split('/').next().unwrap_or(s).to_string())
            .collect();
        Some((status, ips))
    }

}

impl Drop for MeshNode {
    fn drop(&mut self) {
        // Send SIGTERM first to allow graceful cleanup (e.g., interfaces)
        let pgid = format!("-{}", self.process.id());
        let _ = Command::new("sudo").args(["kill", "-TERM", &pgid]).status();
        // Give it a moment to clean up
        std::thread::sleep(Duration::from_millis(500));
        // Then force kill if still running
        let _ = Command::new("sudo").args(["kill", "-9", &pgid]).status();
        let _ = self.process.wait();
    }
}

#[test]
fn test_authorize_member_with_json_config() {
    // Load identities
    let identities: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/tests/fixtures/identities.json")).unwrap()
    ).unwrap();

    let ctrl_secret = identities["controller"]["private"].as_str().unwrap();
    let ctrl_id = ctrl_secret.split(':').next().unwrap();
    let peer_secret = identities["peers"][0]["private"].as_str().unwrap();
    let peer_id = peer_secret.split(':').next().unwrap();

    let network_id = format!("{}000001", ctrl_id);

    // Start controller with whitelist
    let ctrl_config = serde_json::json!({
        "networks": [{ "id": &network_id, "members": [ctrl_id, peer_id] }]
    });
    let controller = MeshNode::spawn("CTRL", ctrl_secret, &[
        ("controller.json", ctrl_config.to_string()),
    ]);

    // Start peer with controller hint
    let peer_config = serde_json::json!({
        "virtual": { ctrl_id: { "role": "UPSTREAM", "try": [format!("127.0.0.1/{}", controller.port)] }}
    });
    let peer = MeshNode::spawn("PEER", peer_secret, &[
        ("local.conf", peer_config.to_string()),
    ]);

    // Expected IPs
    let nwid = u64::from_str_radix(&network_id, 16).unwrap();
    let ctrl_ip = compute_mesh_ip(nwid, u64::from_str_radix(ctrl_id, 16).unwrap());
    let peer_ip = compute_mesh_ip(nwid, u64::from_str_radix(peer_id, 16).unwrap());

    // Both nodes join the network - this triggers peer discovery via try hints
    controller.cli(&["join", &network_id]);
    peer.cli(&["join", &network_id]);

    // Wait for peer authorization
    assert!(
        wait_until(Duration::from_secs(30), || {
            peer.network_status(&network_id)
                .map(|(status, ips)| status == "OK" && ips.contains(&peer_ip.to_string()))
                .unwrap_or(false)
        }),
        "Peer failed to get authorized with expected IP"
    );
    eprintln!("[OK] Peer authorized with {}", peer_ip);

    // Wait for controller authorization
    assert!(
        wait_until(Duration::from_secs(30), || {
            controller.network_status(&network_id)
                .map(|(status, ips)| status == "OK" && ips.contains(&ctrl_ip.to_string()))
                .unwrap_or(false)
        }),
        "Controller failed to get authorized"
    );
    eprintln!("[OK] Controller authorized with {}", ctrl_ip);

    // Verify ping works (retry for DAD completion)
    assert!(
        wait_until(Duration::from_secs(15), || {
            Command::new("ping6").args(["-c", "1", &peer_ip.to_string()]).output().map(|o| o.status.success()).unwrap_or(false)
        }),
        "Failed to ping peer at {}", peer_ip
    );
    eprintln!("[OK] Ping to {} succeeded", peer_ip);
}
