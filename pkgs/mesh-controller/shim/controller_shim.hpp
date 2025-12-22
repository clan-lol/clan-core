/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#ifndef ZT_RUST_CONTROLLER_SHIM_HPP
#define ZT_RUST_CONTROLLER_SHIM_HPP

#include "node/Identity.hpp"
#include "node/NetworkController.hpp"

namespace ZeroTier {

/**
 * Rust-backed network controller implementation
 *
 * This thin C++ shim delegates authorization to Rust code and uses
 * the daemon's infrastructure for signing and sending configs.
 */
class RustController : public NetworkController {
public:
  RustController();
  virtual ~RustController();

  virtual void init(const Identity &signingId, Sender *sender) override;

  virtual void request(uint64_t nwid, const InetAddress &fromAddr,
                       uint64_t requestPacketId, const Identity &identity,
                       const Dictionary<ZT_NETWORKCONFIG_METADATA_DICT_CAPACITY>
                           &metaData) override;

private:
  Identity _signingId;
  Sender *_sender;
  std::string _homePath;
};

} // namespace ZeroTier

#endif // ZT_RUST_CONTROLLER_SHIM_HPP
