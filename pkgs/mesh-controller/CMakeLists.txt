cmake_minimum_required(VERSION 3.16)
project(mesh-controller LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Required: path to upstream source
if(NOT DEFINED SOURCE_DIR)
    message(FATAL_ERROR "SOURCE_DIR must be set to the upstream source directory")
endif()

get_filename_component(SOURCE_DIR "${SOURCE_DIR}" ABSOLUTE)

if(NOT EXISTS "${SOURCE_DIR}/node/Node.cpp")
    message(FATAL_ERROR "SOURCE_DIR does not appear to be valid: ${SOURCE_DIR}")
endif()

message(STATUS "Upstream source: ${SOURCE_DIR}")

# Copy upstream source to build directory and apply patches at configure time
set(PATCHED_SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/zerotier-src")
set(PATCH_FILE "${CMAKE_CURRENT_SOURCE_DIR}/patches/0001-Add-ZT_RUST_CONTROLLER-support-for-pluggable-Rust-ba.patch")

if(NOT EXISTS "${PATCHED_SOURCE_DIR}/.patched")
    message(STATUS "Copying and patching ZeroTier source...")
    file(REMOVE_RECURSE "${PATCHED_SOURCE_DIR}")
    file(COPY "${SOURCE_DIR}/" DESTINATION "${PATCHED_SOURCE_DIR}")
    # Make writable (source may be from read-only Nix store)
    execute_process(
        COMMAND chmod -R u+w "${PATCHED_SOURCE_DIR}"
        RESULT_VARIABLE CHMOD_RESULT
    )
    execute_process(
        COMMAND patch -p1 -i "${PATCH_FILE}"
        WORKING_DIRECTORY "${PATCHED_SOURCE_DIR}"
        RESULT_VARIABLE PATCH_RESULT
    )
    if(NOT PATCH_RESULT EQUAL 0)
        message(FATAL_ERROR "Failed to apply patch")
    endif()
    file(TOUCH "${PATCHED_SOURCE_DIR}/.patched")
endif()

# Use patched source from now on
set(SOURCE_DIR "${PATCHED_SOURCE_DIR}")

# Platform detection
if(APPLE)
    set(PLATFORM "macos")
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.13" CACHE STRING "Minimum macOS version")
elseif(UNIX)
    set(PLATFORM "linux")
else()
    message(FATAL_ERROR "Unsupported platform")
endif()

# Build Rust static library
set(RUST_LIB_NAME "mesh_controller")
set(RUST_TARGET_DIR "${CMAKE_CURRENT_BINARY_DIR}/rust")

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(RUST_PROFILE "debug")
    set(RUST_BUILD_FLAG "")
else()
    set(RUST_PROFILE "release")
    set(RUST_BUILD_FLAG "--release")
endif()

set(RUST_LIB "${RUST_TARGET_DIR}/${RUST_PROFILE}/lib${RUST_LIB_NAME}.a")
add_custom_command(
    OUTPUT "${RUST_LIB}"
    COMMAND ${CMAKE_COMMAND} -E env
        CARGO_TARGET_DIR=${RUST_TARGET_DIR}
        cargo build ${RUST_BUILD_FLAG}
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/Cargo.toml"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/lib.rs"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/config.rs"
    COMMENT "Building Rust controller library"
)
add_custom_target(rust_lib DEPENDS "${RUST_LIB}")

# Core sources
set(ZT_CORE_SOURCES
    ${SOURCE_DIR}/node/AES.cpp
    ${SOURCE_DIR}/node/AES_aesni.cpp
    ${SOURCE_DIR}/node/AES_armcrypto.cpp
    ${SOURCE_DIR}/node/ECC.cpp
    ${SOURCE_DIR}/node/Capability.cpp
    ${SOURCE_DIR}/node/CertificateOfMembership.cpp
    ${SOURCE_DIR}/node/CertificateOfOwnership.cpp
    ${SOURCE_DIR}/node/Identity.cpp
    ${SOURCE_DIR}/node/IncomingPacket.cpp
    ${SOURCE_DIR}/node/InetAddress.cpp
    ${SOURCE_DIR}/node/Membership.cpp
    ${SOURCE_DIR}/node/Metrics.cpp
    ${SOURCE_DIR}/node/Multicaster.cpp
    ${SOURCE_DIR}/node/Network.cpp
    ${SOURCE_DIR}/node/NetworkConfig.cpp
    ${SOURCE_DIR}/node/Node.cpp
    ${SOURCE_DIR}/node/OutboundMulticast.cpp
    ${SOURCE_DIR}/node/Packet.cpp
    ${SOURCE_DIR}/node/Path.cpp
    ${SOURCE_DIR}/node/Peer.cpp
    ${SOURCE_DIR}/node/Poly1305.cpp
    ${SOURCE_DIR}/node/Revocation.cpp
    ${SOURCE_DIR}/node/Salsa20.cpp
    ${SOURCE_DIR}/node/SelfAwareness.cpp
    ${SOURCE_DIR}/node/SHA512.cpp
    ${SOURCE_DIR}/node/Switch.cpp
    ${SOURCE_DIR}/node/Tag.cpp
    ${SOURCE_DIR}/node/Topology.cpp
    ${SOURCE_DIR}/node/Trace.cpp
    ${SOURCE_DIR}/node/Utils.cpp
    ${SOURCE_DIR}/node/Bond.cpp
    ${SOURCE_DIR}/node/PacketMultiplexer.cpp
    ${SOURCE_DIR}/osdep/OSUtils.cpp
)

# service sources
set(ZT_SERVICE_SOURCES
    ${SOURCE_DIR}/osdep/EthernetTap.cpp
    ${SOURCE_DIR}/osdep/ManagedRoute.cpp
    ${SOURCE_DIR}/osdep/Http.cpp
    ${SOURCE_DIR}/service/OneService.cpp
    ${SOURCE_DIR}/ext/http-parser/http_parser.c
)

# Platform-specific sources
if(APPLE)
    list(APPEND ZT_SERVICE_SOURCES
        ${SOURCE_DIR}/osdep/MacEthernetTap.cpp
        ${SOURCE_DIR}/osdep/MacKextEthernetTap.cpp
        ${SOURCE_DIR}/osdep/PortMapper.cpp
    )
    # MacDNSHelper is Objective-C++
    set(ZT_OBJCXX_SOURCES
        ${SOURCE_DIR}/osdep/MacDNSHelper.mm
    )
    # miniupnpc sources
    list(APPEND ZT_SERVICE_SOURCES
        ${SOURCE_DIR}/ext/libnatpmp/natpmp.c
        ${SOURCE_DIR}/ext/libnatpmp/getgateway.c
        ${SOURCE_DIR}/ext/miniupnpc/connecthostport.c
        ${SOURCE_DIR}/ext/miniupnpc/igd_desc_parse.c
        ${SOURCE_DIR}/ext/miniupnpc/minisoap.c
        ${SOURCE_DIR}/ext/miniupnpc/minissdpc.c
        ${SOURCE_DIR}/ext/miniupnpc/miniupnpc.c
        ${SOURCE_DIR}/ext/miniupnpc/miniwget.c
        ${SOURCE_DIR}/ext/miniupnpc/minixml.c
        ${SOURCE_DIR}/ext/miniupnpc/portlistingparse.c
        ${SOURCE_DIR}/ext/miniupnpc/receivedata.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpcommands.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpdev.c
        ${SOURCE_DIR}/ext/miniupnpc/upnperrors.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpreplyparse.c
    )
elseif(UNIX)
    list(APPEND ZT_SERVICE_SOURCES
        ${SOURCE_DIR}/osdep/LinuxEthernetTap.cpp
        ${SOURCE_DIR}/osdep/LinuxNetLink.cpp
        ${SOURCE_DIR}/osdep/PortMapper.cpp
        # UPnP/NAT-PMP support (required for PortMapper symbols)
        ${SOURCE_DIR}/ext/libnatpmp/natpmp.c
        ${SOURCE_DIR}/ext/libnatpmp/getgateway.c
        ${SOURCE_DIR}/ext/miniupnpc/connecthostport.c
        ${SOURCE_DIR}/ext/miniupnpc/igd_desc_parse.c
        ${SOURCE_DIR}/ext/miniupnpc/minisoap.c
        ${SOURCE_DIR}/ext/miniupnpc/minissdpc.c
        ${SOURCE_DIR}/ext/miniupnpc/miniupnpc.c
        ${SOURCE_DIR}/ext/miniupnpc/miniwget.c
        ${SOURCE_DIR}/ext/miniupnpc/minixml.c
        ${SOURCE_DIR}/ext/miniupnpc/portlistingparse.c
        ${SOURCE_DIR}/ext/miniupnpc/receivedata.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpcommands.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpdev.c
        ${SOURCE_DIR}/ext/miniupnpc/upnperrors.c
        ${SOURCE_DIR}/ext/miniupnpc/upnpreplyparse.c
    )
endif()

# Build meshd executable
add_executable(meshd
    ${ZT_CORE_SOURCES}
    ${ZT_SERVICE_SOURCES}
    ${SOURCE_DIR}/one.cpp
    shim/controller_shim.cpp
)

if(APPLE)
    target_sources(meshd PRIVATE ${ZT_OBJCXX_SOURCES})
endif()

target_include_directories(meshd PRIVATE
    ${SOURCE_DIR}
    ${SOURCE_DIR}/ext
    ${SOURCE_DIR}/ext/prometheus-cpp-lite-1.0/core/include
    ${SOURCE_DIR}/ext/prometheus-cpp-lite-1.0/simpleapi/include
    ${SOURCE_DIR}/ext/opentelemetry-cpp-api-only/include
    ${CMAKE_CURRENT_SOURCE_DIR}/shim
)

target_compile_definitions(meshd PRIVATE
    ZT_BUILD_PLATFORM=3
    ZT_BUILD_ARCHITECTURE=2
    ZT_RUST_CONTROLLER
    ZT_USE_MINIUPNPC
    MINIUPNP_STATICLIB
)

if(APPLE)
    target_compile_definitions(meshd PRIVATE
        MACOSX
        _DARWIN_C_SOURCE
        MINIUPNPC_SET_SOCKET_TIMEOUT
        MINIUPNPC_GET_SRC_ADDR
        _BSD_SOURCE
        _DEFAULT_SOURCE
        OS_STRING="Darwin"
        MINIUPNPC_VERSION_STRING="2.0"
        UPNP_VERSION_STRING="UPnP/1.1"
    )
    target_link_libraries(meshd PRIVATE
        "-framework CoreServices"
        "-framework SystemConfiguration"
        "-framework CoreFoundation"
        "-framework Security"
    )
elseif(UNIX)
    target_compile_definitions(meshd PRIVATE
        __LINUX__
        MINIUPNPC_SET_SOCKET_TIMEOUT
        MINIUPNPC_GET_SRC_ADDR
        _BSD_SOURCE
        _DEFAULT_SOURCE
        OS_STRING="Linux"
        MINIUPNPC_VERSION_STRING="2.0"
        UPNP_VERSION_STRING="UPnP/1.1"
    )
    target_link_libraries(meshd PRIVATE pthread)
endif()

# Link Rust library
add_dependencies(meshd rust_lib)
target_link_libraries(meshd PRIVATE "${RUST_LIB}")

# Build MacEthernetTapAgent on macOS (required for creating virtual interfaces)
if(APPLE)
    add_executable(MacEthernetTapAgent
        ${SOURCE_DIR}/osdep/MacEthernetTapAgent.c
    )
    target_compile_definitions(MacEthernetTapAgent PRIVATE
        MACOSX
    )
endif()

# Create symlinks
add_custom_command(TARGET meshd POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink
        meshd mesh-cli
    COMMAND ${CMAKE_COMMAND} -E create_symlink
        meshd mesh-idtool
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Creating symlinks"
)

# Install
install(TARGETS meshd DESTINATION bin)
install(CODE "
    execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink
        meshd \$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/bin/mesh-cli)
    execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink
        meshd \$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/bin/mesh-idtool)
")

# Testing
enable_testing()

# Build Rust tests
set(RUST_TEST_BIN "${RUST_TARGET_DIR}/${RUST_PROFILE}/deps")
add_custom_command(
    OUTPUT "${RUST_TARGET_DIR}/.test_built"
    COMMAND ${CMAKE_COMMAND} -E env
        CARGO_TARGET_DIR=${RUST_TARGET_DIR}
        cargo test --no-run ${RUST_BUILD_FLAG}
    COMMAND ${CMAKE_COMMAND} -E touch "${RUST_TARGET_DIR}/.test_built"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/Cargo.toml"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/lib.rs"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/config.rs"
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/integration_test.rs"
        meshd
    COMMENT "Building Rust integration tests"
)
add_custom_target(rust_tests DEPENDS "${RUST_TARGET_DIR}/.test_built")

add_test(
    NAME integration_test
    COMMAND ${CMAKE_COMMAND} -E env
        "MESH_BIN=${CMAKE_CURRENT_BINARY_DIR}/meshd"
        "CARGO_TARGET_DIR=${RUST_TARGET_DIR}"
        cargo test ${RUST_BUILD_FLAG} -- --test-threads=1 --nocapture
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)
