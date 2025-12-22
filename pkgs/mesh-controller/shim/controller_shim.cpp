/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#include "controller_shim.hpp"

#include "include/ZeroTierOne.h"
#include "node/CertificateOfMembership.hpp"
#include "node/CertificateOfOwnership.hpp"
#include "node/NetworkConfig.hpp"
#include "osdep/OSUtils.hpp"

#include <cstdio>
#include <cstring>

// FFI declarations for Rust functions
extern "C" {
struct AuthResult {
  bool authorized;
  uint8_t ipv6_bytes[16];
};

bool rust_controller_init(uint64_t controller_addr, const char *home_path);
bool rust_controller_reload();
AuthResult rust_check_auth(uint64_t nwid, uint64_t member_addr);
uint64_t rust_controller_address();
}

namespace ZeroTier {

// Default credential time delta (30 minutes)
static const int64_t CREDENTIAL_TIME_MAX_DELTA = 1000LL * 60LL * 30LL;

RustController::RustController() : _sender(nullptr) {}

RustController::~RustController() {}

void RustController::init(const Identity &signingId, Sender *sender) {
  _signingId = signingId;
  _sender = sender;

  // Get home path from environment or use default
  const char *home = getenv("ZT_HOME");
  if (home) {
    _homePath = home;
  } else {
    _homePath = ".";
  }

  uint64_t addr = signingId.address().toInt();
  fprintf(stderr, "[RustController] init: controller=%010llx home=%s\n",
          (unsigned long long)addr, _homePath.c_str());

  if (!rust_controller_init(addr, _homePath.c_str())) {
    fprintf(stderr,
            "[RustController] WARNING: failed to initialize Rust controller\n");
  }
}

void RustController::request(
    uint64_t nwid, const InetAddress &fromAddr, uint64_t requestPacketId,
    const Identity &identity,
    const Dictionary<ZT_NETWORKCONFIG_METADATA_DICT_CAPACITY> &metaData) {
  (void)fromAddr;
  (void)metaData;

  if (!_sender) {
    fprintf(stderr, "[RustController] request: no sender!\n");
    return;
  }

  uint64_t memberAddr = identity.address().toInt();

  fprintf(stderr, "[RustController] request: nwid=%016llx member=%010llx\n",
          (unsigned long long)nwid, (unsigned long long)memberAddr);

  // Check authorization via Rust
  AuthResult result = rust_check_auth(nwid, memberAddr);

  if (!result.authorized) {
    fprintf(stderr, "[RustController] access denied for %010llx\n",
            (unsigned long long)memberAddr);
    _sender->ncSendError(nwid, requestPacketId, identity.address(),
                         NC_ERROR_ACCESS_DENIED, nullptr, 0);
    return;
  }

  // Build network config
  NetworkConfig nc;
  memset(&nc, 0, sizeof(nc));

  nc.networkId = nwid;
  nc.timestamp = OSUtils::now();
  nc.credentialTimeMaxDelta = CREDENTIAL_TIME_MAX_DELTA;
  nc.revision = 1;
  nc.issuedTo = identity.address();
  nc.type = ZT_NETWORK_TYPE_PRIVATE;
  nc.flags = ZT_NETWORKCONFIG_FLAG_ENABLE_BROADCAST |
             ZT_NETWORKCONFIG_FLAG_ENABLE_IPV6_NDP_EMULATION;
  nc.mtu = ZT_DEFAULT_MTU;
  nc.multicastLimit = 32;

  // Network name (optional)
  snprintf(nc.name, sizeof(nc.name), "zt%llx", (unsigned long long)nwid);

  // Single rule: accept all traffic
  nc.ruleCount = 1;
  nc.rules[0].t = ZT_NETWORK_RULE_ACTION_ACCEPT;

  // Assign IPv6 address with /88 prefix (as per InetAddress::makeIpv6rfc4193)
  InetAddress ip6;
  memset(&ip6, 0, sizeof(ip6));
  struct sockaddr_in6 *sin6 = reinterpret_cast<struct sockaddr_in6 *>(&ip6);
  sin6->sin6_family = AF_INET6;
  memcpy(sin6->sin6_addr.s6_addr, result.ipv6_bytes, 16);
  sin6->sin6_port = htons(88); // netmask bits stored in port

  nc.staticIps[0] = ip6;
  nc.staticIpCount = 1;

  // Add route for the /88 network
  nc.routeCount = 1;
  memset(&nc.routes[0], 0, sizeof(nc.routes[0]));
  // Route target: same IP with /88
  struct sockaddr_in6 *routeTarget =
      reinterpret_cast<struct sockaddr_in6 *>(&nc.routes[0].target);
  routeTarget->sin6_family = AF_INET6;
  memcpy(routeTarget->sin6_addr.s6_addr, result.ipv6_bytes, 16);
  // Zero out the host portion (last 40 bits = 5 bytes)
  routeTarget->sin6_addr.s6_addr[11] = 0;
  routeTarget->sin6_addr.s6_addr[12] = 0;
  routeTarget->sin6_addr.s6_addr[13] = 0;
  routeTarget->sin6_addr.s6_addr[14] = 0;
  routeTarget->sin6_addr.s6_addr[15] = 0;
  routeTarget->sin6_port = htons(88); // /88 prefix

  // Certificate of Membership (required for private networks)
  nc.com = CertificateOfMembership(nc.timestamp, CREDENTIAL_TIME_MAX_DELTA,
                                   nwid, identity);
  if (!nc.com.sign(_signingId)) {
    fprintf(stderr, "[RustController] failed to sign COM\n");
    _sender->ncSendError(nwid, requestPacketId, identity.address(),
                         NC_ERROR_INTERNAL_SERVER_ERROR, nullptr, 0);
    return;
  }

  // Certificate of Ownership for assigned IP
  CertificateOfOwnership coo(nwid, nc.timestamp, identity.address(), 1);
  coo.addThing(ip6);
  if (!coo.sign(_signingId)) {
    fprintf(stderr, "[RustController] failed to sign COO\n");
    _sender->ncSendError(nwid, requestPacketId, identity.address(),
                         NC_ERROR_INTERNAL_SERVER_ERROR, nullptr, 0);
    return;
  }
  nc.certificatesOfOwnership[0] = coo;
  nc.certificateOfOwnershipCount = 1;

  fprintf(stderr, "[RustController] sending config to %010llx\n",
          (unsigned long long)memberAddr);

  _sender->ncSendConfig(nwid, requestPacketId, identity.address(), nc, false);
}

} // namespace ZeroTier
