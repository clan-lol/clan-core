#!/usr/bin/env python3

import os
import threading
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    addressof,
    c_char_p,
    c_int,
    c_size_t,
    c_uint8,
    c_void_p,
    cast,
    memmove,
    sizeof,
)
from pathlib import Path
from typing import TypeVar

import libvncclient
from libvncclient import (
    GetCredentialProc,
    GotCursorShapeProc,
    GotFrameBufferUpdateProc,
    GotXCutTextProc,
    HandleKeyboardLedStateProc,
    HandleRFBServerMessage,
    MallocFrameBufferProc,
    SendFramebufferUpdateRequest,
    SetFormatAndEncodings,
    String,
    WaitForMessage,
    rfbClient,
    rfbClientCleanup,
    rfbCredential,
    rfbCredentialTypeUser,
    rfbCredentialTypeX509,
    rfbGetClient,
    rfbInitClient,
    struct__rfbClient,
)

path_to_lib = libvncclient._libs["libvncclient.so"].access["cdecl"]._name
if path_to_lib.startswith("/nix/store/"):
    print("Using libvncclient from nix store")
    exit(-1)


libc = CDLL("libc.so.6")  # Use the correct path for your libc
libc.malloc.argtypes = [c_size_t]
libc.malloc.restype = c_void_p


def alloc_str(data: str) -> c_char_p:
    bdata = data.encode("ascii") + b"\0"
    data_buf = libc.malloc(len(bdata))  # +1 for null terminator

    memmove(data_buf, c_char_p(bdata), len(bdata))

    return data_buf


StructType = TypeVar("StructType", bound="Structure")


def got_cursor_shape(
    cl: rfbClient,
    width: int,
    height: int,
    xhot: int,
    yhot: int,
    data: POINTER(c_uint8),  # type: ignore[valid-type]
) -> None:
    print(f"got_cursor_shape: {width} {height} {xhot} {yhot}")
    return


def alloc_struct(data: StructType) -> int:
    data_buf = libc.malloc(sizeof(data))
    memmove(data_buf, addressof(data), sizeof(data))
    return data_buf


def get_credential(
    rfb_client: POINTER(struct__rfbClient),  # type: ignore[valid-type]
    credential_type: c_int,
) -> int | None:
    print(f"==> get_credential: {credential_type}")

    if credential_type == rfbCredentialTypeUser:
        creds = rfbCredential()
        username = os.environ.get("USER")
        if not username:
            print("ERROR: USER environment variable is not set")
            return None
        creds.userCredential.username = alloc_str(username)
        creds.userCredential.password = None
        creds_buf = alloc_struct(creds)

        # Return a integer to the creds obj
        return creds_buf

    if credential_type == rfbCredentialTypeX509:
        ca_dir = (
            Path(os.environ.get("GIT_ROOT", ""))
            / "pkgs"
            / "clan-vm-manager"
            / "tests"
            / "data"
            / "vnc-security"
        )
        ca_cert = ca_dir / "ca.crt"
        if not ca_cert.exists():
            print(f"ERROR: ca_cert does not exist: {ca_cert}")
            return None
        ca_crl = ca_dir / "ca.key"
        if not ca_crl.exists():
            print(f"ERROR: ca_crl does not exist: {ca_crl}")
            return None

        # Instantiate the credential union and populate it
        creds = rfbCredential()
        creds.x509Credential.x509CACertFile = alloc_str(str(ca_cert))
        creds.x509Credential.x509CrlVerifyMode = False
        print("===> Alloc struct")
        creds_buf = alloc_struct(creds)
        print("====> Done alloc struct")

        # Return a integer to the creds obj
        return creds_buf

    print(f"ERROR: Unknown credential type: {credential_type}")
    return None


def got_selection(cl: rfbClient, text: str, text_len: int) -> None:
    print(f"got_selection: {text}")


def resize(client: rfbClient) -> bool:
    width = client.contents.width
    height = client.contents.height
    bits_per_pixel = client.contents.format.bitsPerPixel
    print(f"Size: {width}x{height}")

    if client.contents.frameBuffer:
        libc.free(client.contents.frameBuffer)
        client.contents.frameBuffer = None

    new_buf = libc.malloc(int(width * height * bits_per_pixel / 8))
    if not new_buf:
        print("malloc failed")
        return False

    casted_buf = cast(new_buf, POINTER(c_uint8))
    client.contents.frameBuffer = casted_buf

    request = SendFramebufferUpdateRequest(client, 0, 0, width, height, False)
    if not request:
        print("SendFramebufferUpdateRequest failed")

    return True


def update(cl: rfbClient, x: int, y: int, w: int, h: int) -> None:
    print(f"update: {x} {y} {w} {h}")
    return


def kbd_leds(cl: rfbClient, value: int, pad: int) -> None:
    print(f"kbd_leds: {value} {pad}")


# /*****************************************************************************
#  *
#  * Encoding types
#  *
#  *****************************************************************************/

# #define rfbEncodingRaw 0
# #define rfbEncodingCopyRect 1
# #define rfbEncodingRRE 2
# #define rfbEncodingCoRRE 4
# #define rfbEncodingHextile 5
# #define rfbEncodingZlib 6
# #define rfbEncodingTight 7
# #define rfbEncodingTightPng 0xFFFFFEFC /* -260 */
# #define rfbEncodingZlibHex 8
# #define rfbEncodingUltra 9
# #define rfbEncodingTRLE 15
# #define rfbEncodingZRLE 16
# #define rfbEncodingZYWRLE 17

# #define rfbEncodingH264               0x48323634

# /* Cache & XOR-Zlib - rdv@2002 */
# #define rfbEncodingCache                 0xFFFF0000
# #define rfbEncodingCacheEnable           0xFFFF0001
# #define rfbEncodingXOR_Zlib              0xFFFF0002
# #define rfbEncodingXORMonoColor_Zlib     0xFFFF0003
# #define rfbEncodingXORMultiColor_Zlib    0xFFFF0004
# #define rfbEncodingSolidColor            0xFFFF0005
# #define rfbEncodingXOREnable             0xFFFF0006
# #define rfbEncodingCacheZip              0xFFFF0007
# #define rfbEncodingSolMonoZip            0xFFFF0008
# #define rfbEncodingUltraZip              0xFFFF0009


class VncError(Exception):
    pass


class VncClient:
    client: rfbClient
    stop_event: threading.Event
    thread: threading.Thread | None

    def __init__(self) -> None:
        bits_per_sample = 8
        samples_per_pixel = 3
        bytes_per_pixel = 4
        self.client: rfbClient = rfbGetClient(
            bits_per_sample, samples_per_pixel, bytes_per_pixel
        )
        if not self.client:
            raise VncError("rfbGetClient failed")

        self.stop_event = threading.Event()  # Initialize the stop event.
        self.thread = None

        self._client_settings()
        self._set_color()
        self._set_encoding()

    def _client_settings(self) -> None:
        # client settings
        self.client.contents.MallocFrameBuffer = MallocFrameBufferProc(resize)
        self.client.contents.canHandleNewFBSize = True
        self.client.contents.GotFrameBufferUpdate = GotFrameBufferUpdateProc(update)
        self.client.contents.HandleKeyboardLedState = HandleKeyboardLedStateProc(
            kbd_leds
        )
        self.client.contents.GotXCutText = GotXCutTextProc(got_selection)
        self.client.contents.GotCursorShape = GotCursorShapeProc(got_cursor_shape)
        self.client.contents.GetCredential = GetCredentialProc(get_credential)
        self.client.contents.listenPort = 5900
        self.client.contents.listenAddress = String.from_param("127.0.0.1")

    def _set_color(self) -> None:
        # Set client encoding to (equal to remmina)
        # TRUE colour: max red 255 green 255 blue 255, shift red 16 green 8 blue 0
        self.client.contents.format.bitsPerPixel = 32
        self.client.contents.format.depth = 24
        self.client.contents.format.redShift = 16
        self.client.contents.format.blueShift = 0
        self.client.contents.format.greenShift = 8
        self.client.contents.format.blueMax = 0xFF
        self.client.contents.format.redMax = 0xFF
        self.client.contents.format.greenMax = 0xFF
        SetFormatAndEncodings(self.client)

    def _set_encoding(self) -> None:
        # Set client compression to remminas quality 9 (best) and compress level 1 (lowest)
        # BUG: tight encoding is crashing (looks exploitable)
        self.client.contents.appData.shareDesktop = True
        self.client.contents.appData.useBGR233 = False
        self.client.contents.appData.encodingsString = String.from_param(
            "copyrect zlib hextile raw"
        )
        self.client.contents.appData.compressLevel = 1
        self.client.contents.appData.qualityLevel = 9
        SetFormatAndEncodings(self.client)

    def start_blocking(self) -> None:
        print("Initializing connection")
        argc = c_int(0)
        argv = None
        if not rfbInitClient(self.client, argc, argv):
            raise VncError("rfbInitClient failed")

        # Main loop
        while not self.stop_event.is_set():
            res = WaitForMessage(self.client, 500)
            if res < 0:
                rfbClientCleanup(self.client)
                raise VncError("WaitForMessage failed")

            if res > 0:
                if not HandleRFBServerMessage(self.client):
                    rfbClientCleanup(self.client)
                    raise VncError("HandleRFBServerMessage failed")

        rfbClientCleanup(self.client)

    def start(self) -> None:
        self.thread = threading.Thread(target=self.start_blocking)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()  # Signal the thread to stop.
        if self.thread is not None:
            self.thread.join()  # Wait for the thread to finish.
        print("VNC client stopped.")


if __name__ == "__main__":
    vnc = VncClient()
    vnc.start()
    assert vnc.thread is not None
    vnc.thread.join()
