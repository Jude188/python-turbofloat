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

from ctypes import pointer, sizeof, c_uint32

from turbofloat.c_wrapper import *

#
# Object oriented interface
#

class TurboFloat(object):

    def __init__(self, dat_file, guid, library_folder="", mode=TA_USER):
        self._lib = load_library(library_folder)
        self._set_restype()

        self._mode = mode
        self._dat_file = wstr(dat_file)
        self._callback = None

        try:
            self._lib.TF_PDetsFromPath(self._dat_file)
        except TurboFloatFailError:
            # The dat file is already loaded
            pass

        self._handle = self._lib.TF_GetHandle(wstr(guid))

        # if the handle is still unset then immediately throw an exception
        # telling the user that they need to actually load the correct
        # TurboActivate.dat and/or use the correct GUID for the TurboActivate.dat
        if self._handle == 0:
            raise TurboFloatDatFileError()

        self._callback = None

    #
    # Public
    #

    # TurboFloat server

    def save_server(self, host_address, port):
        """
        Saves the TurboFloat server location on the disk. You must call this function at
         least once before requesting a lease from the server. A good place to call this function
        is from your installer (so an IT admin could set the server location once).


        Note: If you pass in the TF_SYSTEM flag and you don't have "admin" or "elevated"
        permission then the call will fail.

        If you call this function once in the past with the flag TF_SYSTEM and the calling
        process was an admin process then subsequent calls with the TF_SYSTEM flag will
        succeed even if the calling process is *not* admin/elevated.

        If you want to take advantage of this behavior from an admin process
        (e.g. an installer) but the user hasn't entered a product key then you can
        call this function with a null string:

            TF_SaveServer(YourHandle, 0, 0, TF_SYSTEM);

        This will set everything up so that subsequent calls with the TF_SYSTEM flag will
        succeed even if from non-admin processes.
        """

        args = []
        args.append(wstr(host_address))
        args.append(port)
        args.append(self._mode)

        try:
            self._lib.TF_SaveServer(self._handle, *args)
        except TurboFloatError as e:
            raise e

    def get_server(self, port):
        """Gets the stored TurboFloat Server location."""

        buf_size = 255
        buf = wbuf(buf_size)

        try:
            self._lib.TF_GetServer(self._handle, buf, buf_size, *port)

            return buf.value
        except TurboActivateFailError as e:
            raise e

    # Set Lease Callback function

    def set_callback(self, callback):
        """
        Set the function that will be called by a separate background thread that notifies
        your app of lease events (e.g. the lease expired, the features changed, etc.).

        If there's a lease currently assigned to your app, then you won't be able to change
        the callback until either the lease expires (and can't be renewed) or until you
        drop the lease by calling the drop_lease() function.

        The lease callback function should handle everything defined below (see:
        "Possible callback statuses" at the bottom of this header). Everything that's
        not defined should be handled as a failure to renew the lease.
        """

        self._callback = LeaseCallbackType(callback)

        try:
            self._lib.TF_SetLeaseCallback(self._handle, self._callback)
        except TurboFloatError as e:
            raise e

    def set_callback(self, callback):
        """
        Set the function that will be called by a separate background thread that notifies
        your app of lease events (e.g. the lease expired, the features changed, etc.).

        TF_SetLeaseCallbackEx() also allow you to pass allong "context" in the form
        of a pointer that you defined. This is passed back along by the TurboFloat
        Library when the callback function is called.

        If there's a lease currently assigned to your app, then you won't be able to change
        the callback until either the lease expires (and can't be renewed) or until you
        drop the lease by calling the TF_DropLease() function.

        The lease callback function should handle everything defined below (see:
        "Possible callback statuses" at the bottom of this header). Everything that's
        not defined should be handled as a failure to renew the lease.
        """

        self._callback = LeaseCallbackTypeEx(callback)

        try:
            self._lib.TF_SetLeaseCallbackEx(self._handle, self._callback)
        except TurboFloatError as e:
            raise e

    # Leases

    def request_lease(self):
        """
        Requests a floating license lease from the TurboFloat Server. You should run
        this at the top of your app after calling set_callback().
        """

        try:
            self._lib.TF_RequestLease(self._handle)
        except TurboFloatError as e:
            raise e

    def drop_lease(self):
        """
        Drops the active lease from the TurboFloat Server. This frees up the lease
        so it can be used by another instance of your app.

        We recommend calling this before your application exits.

        Note: This function does *not* call the lease callback function. If you want that
            behavior then you can do it like this:


            if (TF_DropLease(tfHandle) == TF_OK)
            {
                YourLeaseCallbackFunction(TF_CB_EXPIRED);
            }
        """

        try:
            self._lib.TF_DropLease(self._handle)
        except TurboFloatError as e:
            raise e

        pass

    def has_lease(self):
        """
        Let's you know whether there's an active lease for the handle specified. This function
        isn't necessary if you're tracking the responses from request_lease(), drop_lease(),
        and the callback function that you set in set_callback().
        """

        ret = self._lib.TF_HasLease(self._handle)

        if ret == TA_OK:
            return True
        elif ret == TA_FAIL:
            return False

        # raise an error on all other return codes
        validate_result(ret)

    # Features

    def has_feature(self, name):
        return len(self.get_feature_value(name)) > 0

    def get_feature_value(self, name):
        """Gets the value of a feature."""
        buf_size = self._lib.TF_GetFeatureValue(self._handle, wstr(name), 0, 0)
        buf = wbuf(buf_size)

        self._lib.TF_GetFeatureValue(self._handle, wstr(name), buf, buf_size)

        return buf.value


    # Utils

    def is_date_valid(self, date):
        """
        Check if the date is valid
        """

        try:
            self._lib.TF_IsDateValid(self._handle, wstr(date), TF_HAS_NOT_EXPIRED)

            return True
        except TurboFloatFlagsError as e:
            raise e
        except TurboFloatError:
            return False

    def clean_up(self):
        """
        You should call this before your application exits. This frees up any
        allocated memory for all open handles. If you have an active license
        lease then you should call drop_lease() before you call clean_up().
        """

        try:
            self._lib.TF_Cleanup()
        except TurboFloatError as e:
            rasie e

    def _set_restype(self):
        self._lib.TF_SaveServer = validate_result
        self._lib.TF_SetLeaseCallback = validate_result
        self._lib.TF_RequestLease = validate_result
        self._lib.TF_DropLease = validate_result
        self._lib.TF_GetFeatureValue.restype = validate_result
        self._lib.TF_GetServer.restype = validate_result
        self._lib.TF_PDetsFromPath.restype = validate_result
        self._lib.TF_Cleanup.restype = validate_result
        self._lib.TF_IsDateValid.restype = validate_result
