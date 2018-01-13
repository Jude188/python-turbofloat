# -*- coding: utf-8 -*-
#
# Copyright 2018 Open Broadcast Systems Ltd. (https://www.obe.tv/)
#
# Author: Judah Rand <judahrand@obe.tv>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import sys
from os import path as ospath
from ctypes import (
    cdll,
    c_uint,
    c_void_p,
    c_char_p,
    c_wchar_p,
    Structure,
    create_string_buffer,
    create_unicode_buffer,
    CFUNCTYPE
)

# Utilities

wbuf = create_unicode_buffer if sys.platform == "win32" else create_string_buffer

wstr = c_wchar_p if sys.platform == "win32" else c_char_p

# Wrapper

TF_OK = 0x00000000
TF_FAIL = 0x00000001
TF_E_SERVER = 0x00000002
TF_E_NO_CALLBACK = 0x00000003
TF_E_INET = 0x00000004
TF_E_NO_FREE_LEASES = 0x00000005
TF_E_LEASE_EXISTS = 0x00000006
TF_E_WRONG_TIME = 0x00000007
TF_E_PDETS = 0x00000008
TF_E_INVALID_HANDLE = 0x00000009
TF_E_NO_LEASE = 0x0000000A
TF_E_COM = 0x0000000B
TF_E_INSUFFICIENT_BUFFER = 0x0000000C
TF_E_PERMISSION = 0x0000000D
TF_E_INVALID_FLAGS = 0x0000000E
TF_E_WRONG_SERVER_PRODUCT = 0x0000000F
TF_E_INET_TIMEOUT = 0x00000010
TF_E_UPGRADE_LIBRARY = 0x00000011
TF_E_USERNAME_NOT_ALLOWED = 0x00000012
TF_E_ENABLE_NETWORK_ADAPTERS = 0x0000001C


# Flags for the UseTrial() and CheckAndSavePKey() functions.

TF_SYSTEM = 0x00000001
TF_USER = 0x00000002


# Flags for callback status.

"""
Called when the lease has expired and couldn't be renewed. You
should disable your app immediately when this return code is called.
Of course give your user a way to save the current state of their
data and/or request a lease renewal from the server.

In other words, don't make the user mad. Make sure you test this
extensively with real end-users so you get the best behavior.
"""
TF_CB_EXPIRED = 0x00000000

"""
Called when the lease has expired and couldn't be renewed due to
failure to connect to the TurboFloat Server.
"""
TF_CB_EXPIRED_INET = 0x00000001

"""
Called when the lease was renewed and some or all of the custom
license fields have since changed. If you use the TF_GetFeatureValue()
function then it behooves you to get the latest changed feature
values upon this callback status.
"""
TF_CB_FEATURES_CHANGED = 0x00000002


# Flags for the TF_IsDateValid() function.

"""
With this flag, TF_IsDateValid() will return TA_OK if the passed in "date_time"
has not expired and the system dates have not been tampered with. Otherwise,
TA_FAIL will be returned.
"""
TF_HAS_NOT_EXPIRED = 0x00000001

# Types for callback functions.

"""
The lease callback function type.
"""
LeaseCallbackType = CFUNCTYPE(c_void_p, c_uint)

"""
The lease callback function type with a user-defined pointer.
"""
LeaseCallbackTypeEx = CFUNCTYPE(c_void_p, c_uint, c_void_p)


def load_library(path):

    if sys.platform == 'win32':
        return cdll.LoadLibrary(ospath.join(path, 'TurboFloat.dll'))
    elif sys.platform == 'darwin':
        return cdll.LoadLibrary(ospath.join(path, 'libTurboFloat.dylib'))

    # else: linux, bsd, etc.
    return cdll.LoadLibrary(ospath.join(path, 'libTurboFloat.so'))


def validate_result(return_code):
    # All ok, no need to perform error handling.
    if return_code == TF_OK:
        return

    # Raise an exception type appropriate for the kind of error
    if return_code == TF_FAIL:
        raise TurboFloatFailError()
    elif return_code == TF_E_SERVER:
        raise TurboFloatNoServerError()
    elif return_code == TF_E_NO_CALLBACK:
        raise TurboFloatNoCallbackError()
    elif return_code == TF_E_INET:
        raise TurboFloatConnectionError()
    elif return_code == TF_E_NO_FREE_LEASES:
        raise TurboFloatNoFreeLeaseError()
    elif return_code == TF_E_LEASE_EXISTS:
        raise TurboFloatLeaseAquiredError()
    elif return_code == TF_E_WRONG_TIME:
        raise TurboFloatTimeError()
    elif return_code == TF_E_PDETS:
        raise TurboFloatDatFileError()
    elif return_code == TF_E_INVALID_HANDLE:
        raise TurboFloatInvalidHandleError()
    elif return_code == TF_E_NO_LEASE:
        raise TurboFloatNoLeaseError()
    elif return_code == TF_E_COM:
        raise TurboFloatComError()
    elif return_code == TF_E_INSUFFICIENT_BUFFER:
        raise TurboFloatBufferError()
    elif return_code == TF_E_PERMISSION:
        raise TurboFloatPermissionError()
    elif return_code == TF_E_INVALID_FLAGS:
        raise TurboFloatFlagsError()
    elif return_code == TF_E_WRONG_SERVER_PRODUCT:
        raise TurboFloatWrongServerProductError()
    elif return_code == TF_E_INET_TIMEOUT:
        raise TurboFloatConnectionTimeoutError()
    elif return_code == TF_E_UPGRADE_LIBRARY:
        raise TurboFloatUpgradeLibraryError()
    elif return_code == TF_E_USERNAME_NOT_ALLOWED:
        raise TurboFloatUsernameNotAllowedError()
    elif return_code == TF_E_ENABLE_NETWORK_ADAPTERS:
        raise TurboFloatEnableNetworkAdaptersError()

    # Otherwise bail out and raise a generic exception
    raise TurboActivateError(return_code)


#
# Exception types
#

class TurboFloatError(Exception):

    """Generic TurboActivate error"""
    pass


class TurboFloatFailError(TurboFloatError):

    """Fail error"""
    pass


class TurboFloatNoServerError(TurboFloatError):

    """There's no server specified. You must call TF_SaveServer() at least once to save the server."""
    pass


class TurboFloatConnectionError(TurboFloatError):

    """Connection to the TurboFloat server failed."""
    pass


class TurboFloatNoCallbackError(TurboFloatError):

    """You didn't specify a callback. Do so using the TF_SetLeaseCallback() or TF_SetLeaseCallbackEx() function."""
    pass


class TurboFloatNoFreeLeaseError(TurboFloatError):

    """
    There are no more free leases available from the TurboFloat server. Either
    increase the number of allowed floating licenses for the TurboFloat server
    or wait for one of the other leases to expire.
    """
    pass


class TurboFloatLeaseAquiredError(TurboFloatError):

    """
    The lease has already been acquired. TurboFloat automatically renews the lease
    when it needs to based on the information the TurboFloat Server provides.
    """
    pass


class TurboFloatTimeError(TurboFloatError):

    """
    The product details file "TurboActivate.dat" failed to load.

    On Windows the TurboActivate.dat must be in the same folder as the TurboFloat.dll file.
    On Unix (Linux / Mac OS X / etc.) the TurboActivate.dat file must be in the same
    folder as the executable calling the TurboFloat functions. Also, on Windows,
    if you're using static linking with the TurboFloat library then the TurboActivate.dat
    must be in the same folder as the executable (or DLL) using the TurboFloat library
    functions.

    On Mac OS X this can be confusing because a ".app" file isn't really a file
    at all, it's just a folder (or "bundle") that contains assets, and a few levels
    of directories like this:

    MyApp.app/
        Contents/
            Info.plist
            MacOS/
            Resources/

    In a Mac OS X application bundle the "actual executable" is inside the "MacOS"
    folder. That's where your should put TurboActivate.dat.


    If you can't or don't want to include TurboActivate.dat alongside TurboFloat.dll
    on Windows or alongside your app on Unix, or you just want to rename TurboActivate.dat
    to something else, then your only option is to call TF_PDetsFromPath().
    """
    pass


class TurboFloatDatFileError(TurboFloatError):

    """The handle is not valid. To get a handle use TF_GetHandle()."""
    pass


class TurboFloatInvalidHandleError(TurboFloatError):

    """
    There's no lease. Your must first have a lease before you can
    drop it or get information on it.
    """
    pass


class TurboFloatNoLeaseError(TurboFloatError):

    """
    There's no lease. Your must first have a lease before you can
    drop it or get information on it.
    """
    pass

class TurboFloatComError(TurboFloatError):

    """
    The hardware id couldn't be generated due to an error in the COM setup.
    Re-enable Windows Management Instrumentation (WMI) in your group policy
    editor or reset the local group policy to the default values. Contact
    your system admin for more information.

    This error is Windows only.

    This error can also be caused by the user (or another program) disabling
    the "Windows Management Instrumentation" service. Make sure the "Startup type"
    is set to Automatic and then start the service.


    To further debug WMI problems open the "Computer Management" (compmgmt.msc),
    expand the "Services and Applications", right click "WMI Control" click
    "Properties" and view the status of the WMI.
    """
    pass


class TurboFloatBufferError(TurboFloatError):

    """The the buffer size was too small. Create a larger buffer and try again."""
    pass


class TurboFloatPermissionError(TurboFloatError):

    """
    Insufficient system permission. Either start your process as an
    admin / elevated user or call the function again with the
    TF_USER flag instead of the TF_SYSTEM flag.
    """
    pass


class TurboFloatFlagsError(TurboFloatError):

    """
    The flags you passed to SaveServer(...) were invalid or missing.
    Flags like "TF_SYSTEM" and "TF_USER" are mutually exclusive --
    you can only use one or the other.
    """
    pass


class TurboFloatWrongServerProductError(TurboFloatError):

    """
    The TurboFloat Server you're trying to contact can't give license
    leases for this product version.
    """
    pass


class TurboFloatConnectionTimeoutError(TurboFloatError):

    """
    The connection to the server timed out because a long period of time
    elapsed since the last data was sent or recieved.
    """
    pass


class TurboFloatUpgradeLibraryError(TurboFloatError):

    """
    The TurboFloat Library you're currently using cannot be used
    to communicate with the TurboFloat Server instance. Release a new
    version of your app with the latest version of the TurboFloat Library.

    Get it here: https://wyday.com/limelm/api/#turbofloat
    """
    pass


class TurboFloatUsernameNotAllowedError(TurboFloatError):

    """
    The current user cannot request a license lease from the server because
    their username has not been added to the whitelist of approved usernames.
    """
    pass

class TurboFloatEnableNetworkAdaptersError(TurboFloatError):

    """
    There are network adapters on the system that are disabled and
    TurboFloat couldn't read their hardware properties (even after trying
    and failing to enable the adapters automatically). Enable the network adapters,
    re-run the function, and TurboFloat will be able to "remember" the adapters
    even if the adapters are disabled in the future.

    Note: The network adapters do not need an active Internet connections. They just
          need to not be disabled. Whether they are or are not connected to the
          internet/intranet is not important and does not affect this error code at all.


    On Linux you'll get this error if you don't have any real network adapters attached.
    For example if you have no "eth[x]", "wlan[x]", "en[x]", "wl[x]", "ww[x]", or "sl[x]"
    network interface devices.

    See: https://wyday.com/limelm/help/faq/#disabled-adapters
    """
    pass


class TurboFloatLeaseExpired(TurboFloatError):
    pass

class TurboFloatFeatureChange(TurboFloatError):
    pass
