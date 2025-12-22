//! Minimal Network Mesh Controller in Rust
//!
//! This implements a simple whitelist-based controller that:
//! - Reads authorized members from controller.json
//! - Assigns deterministic IPv6 addresses
//! - Issues signed network configurations

pub mod config;

use config::ControllerConfig;
use std::ffi::{c_char, CStr};
use std::net::Ipv6Addr;
use std::path::PathBuf;
use std::sync::Mutex;

/// Global controller state
static CONTROLLER: Mutex<Option<Controller>> = Mutex::new(None);

struct Controller {
    config: ControllerConfig,
    controller_addr: u64,
    home_path: PathBuf,
}

/// Compute deterministic IPv6 address from network and node IDs
///
/// Format: fd{network_id}:9993:{node_id}
fn compute_mesh_ip(network_id: u64, node_id: u64) -> Ipv6Addr {
    let bytes: [u8; 16] = [
        0xFD,
        ((network_id >> 56) & 0xFF) as u8,
        ((network_id >> 48) & 0xFF) as u8,
        ((network_id >> 40) & 0xFF) as u8,
        ((network_id >> 32) & 0xFF) as u8,
        ((network_id >> 24) & 0xFF) as u8,
        ((network_id >> 16) & 0xFF) as u8,
        ((network_id >> 8) & 0xFF) as u8,
        (network_id & 0xFF) as u8,
        0x99,
        0x93,
        ((node_id >> 32) & 0xFF) as u8,
        ((node_id >> 24) & 0xFF) as u8,
        ((node_id >> 16) & 0xFF) as u8,
        ((node_id >> 8) & 0xFF) as u8,
        (node_id & 0xFF) as u8,
    ];
    Ipv6Addr::from(bytes)
}

/// Result of authorization check
#[repr(C)]
pub struct AuthResult {
    pub authorized: bool,
    pub ipv6_bytes: [u8; 16],
}

/// Initialize the Rust controller
///
/// # Safety
/// `home_path` must be a valid null-terminated C string
#[no_mangle]
pub unsafe extern "C" fn rust_controller_init(
    controller_addr: u64,
    home_path: *const c_char,
) -> bool {
    if home_path.is_null() {
        eprintln!("rust_controller_init: home_path is null");
        return false;
    }

    let home_str = match CStr::from_ptr(home_path).to_str() {
        Ok(s) => s,
        Err(e) => {
            eprintln!("rust_controller_init: invalid home_path: {}", e);
            return false;
        }
    };

    let home = PathBuf::from(home_str);
    let config_path = home.join("controller.json");

    eprintln!(
        "rust_controller_init: controller={:010x}, config={}",
        controller_addr,
        config_path.display()
    );

    let config = match ControllerConfig::load(&config_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("rust_controller_init: failed to load config: {}", e);
            return false;
        }
    };

    let mut guard = CONTROLLER.lock().unwrap();
    *guard = Some(Controller {
        config,
        controller_addr,
        home_path: home,
    });

    eprintln!("rust_controller_init: initialized successfully");
    true
}

/// Reload configuration from disk
#[no_mangle]
pub extern "C" fn rust_controller_reload() -> bool {
    let mut guard = CONTROLLER.lock().unwrap();
    let controller = match guard.as_mut() {
        Some(c) => c,
        None => {
            eprintln!("rust_controller_reload: not initialized");
            return false;
        }
    };

    let config_path = controller.home_path.join("controller.json");
    match ControllerConfig::load(&config_path) {
        Ok(c) => {
            controller.config = c;
            eprintln!("rust_controller_reload: reloaded successfully");
            true
        }
        Err(e) => {
            eprintln!("rust_controller_reload: failed: {}", e);
            false
        }
    }
}

/// Check if a member is authorized and get their IP
#[no_mangle]
pub extern "C" fn rust_check_auth(nwid: u64, member_addr: u64) -> AuthResult {
    let guard = CONTROLLER.lock().unwrap();
    let controller = match guard.as_ref() {
        Some(c) => c,
        None => {
            eprintln!("rust_check_auth: not initialized");
            return AuthResult {
                authorized: false,
                ipv6_bytes: [0; 16],
            };
        }
    };

    // Check if we manage this network
    if !controller.config.manages_network(nwid, controller.controller_addr) {
        return AuthResult {
            authorized: false,
            ipv6_bytes: [0; 16],
        };
    }

    // Check if member is authorized
    if !controller.config.is_authorized(nwid, member_addr) {
        eprintln!(
            "rust_check_auth: member {:010x} not authorized for {:016x}",
            member_addr,
            nwid
        );
        return AuthResult {
            authorized: false,
            ipv6_bytes: [0; 16],
        };
    }

    // Compute deterministic IP
    let ip = compute_mesh_ip(nwid, member_addr);
    eprintln!(
        "rust_check_auth: authorized {:010x} for {:016x} -> {}",
        member_addr,
        nwid,
        ip
    );

    AuthResult {
        authorized: true,
        ipv6_bytes: ip.octets(),
    }
}

/// Get the controller address (for verification)
#[no_mangle]
pub extern "C" fn rust_controller_address() -> u64 {
    let guard = CONTROLLER.lock().unwrap();
    guard.as_ref().map(|c| c.controller_addr).unwrap_or(0)
}
