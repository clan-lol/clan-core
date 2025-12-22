//! Configuration loading for the mesh controller

use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Deserialize)]
pub struct NetworkConfig {
    pub id: String,
    pub members: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub networks: Vec<NetworkConfig>,
}

#[derive(Debug, Clone)]
pub struct ControllerConfig {
    networks: HashMap<u64, HashSet<u64>>,
}

impl ControllerConfig {
    pub fn load<P: AsRef<Path>>(path: P) -> Result<Self, String> {
        let content = fs::read_to_string(path.as_ref())
            .map_err(|e| format!("Failed to read config file: {}", e))?;
        Self::from_json(&content)
    }

    pub fn from_json(json: &str) -> Result<Self, String> {
        let config: Config =
            serde_json::from_str(json).map_err(|e| format!("Failed to parse config: {}", e))?;

        let mut networks = HashMap::new();
        for network in config.networks {
            let nwid = parse_network_id(&network.id)?;
            let mut members = HashSet::new();
            for member in &network.members {
                let addr = parse_address(member)?;
                members.insert(addr);
            }
            networks.insert(nwid, members);
        }
        Ok(ControllerConfig { networks })
    }

    pub fn is_authorized(&self, nwid: u64, member_addr: u64) -> bool {
        self.networks
            .get(&nwid)
            .map(|members| members.contains(&member_addr))
            .unwrap_or(false)
    }

    pub fn manages_network(&self, nwid: u64, controller_addr: u64) -> bool {
        let nwid_controller = nwid >> 24;
        nwid_controller == controller_addr && self.networks.contains_key(&nwid)
    }
}

fn parse_network_id(s: &str) -> Result<u64, String> {
    if s.len() != 16 {
        return Err(format!("Network ID must be 16 hex chars, got {}", s.len()));
    }
    u64::from_str_radix(s, 16).map_err(|e| format!("Invalid network ID '{}': {}", s, e))
}

fn parse_address(s: &str) -> Result<u64, String> {
    if s.len() != 10 {
        return Err(format!("Address must be 10 hex chars, got {}", s.len()));
    }
    u64::from_str_radix(s, 16).map_err(|e| format!("Invalid address '{}': {}", s, e))
}
