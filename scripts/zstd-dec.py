#!/usr/bin/env python3
"""Decompress .zst via ctypes libzstd streaming API (handles unknown frame size).
Usage: zstd-dec.py in.zst out.tar"""
import ctypes, sys

lib = ctypes.CDLL("libzstd.so.1")
lib.ZSTD_createDStream.restype = ctypes.c_void_p
lib.ZSTD_initDStream.restype = ctypes.c_size_t
lib.ZSTD_decompressStream.restype = ctypes.c_size_t
lib.ZSTD_isError.restype = ctypes.c_uint
lib.ZSTD_freeDStream.restype = ctypes.c_size_t

data = open(sys.argv[1], "rb").read()
dctx = lib.ZSTD_createDStream()
lib.ZSTD_initDStream(dctx)

IN, OUT = 1 << 20, 1 << 20
src = ctypes.create_string_buffer(data, len(data))
dst = ctypes.create_string_buffer(OUT)
pos, out_path = 0, []
srcbuf = ctypes.cast(src, ctypes.POINTER(ctypes.c_char))
with open(sys.argv[2], "wb") as f:
    while pos < len(data):
        srcp = ctypes.cast(ctypes.byref(src, pos), ctypes.POINTER(ctypes.c_char))
        in_sz, out_sz = ctypes.c_size_t(len(data) - pos), ctypes.c_size_t(OUT)
        r = lib.ZSTD_decompressStream(dctx, ctypes.cast(dst, ctypes.POINTER(ctypes.c_char)), ctypes.byref(out_sz),
                                      srcp, ctypes.byref(in_sz))
        if lib.ZSTD_isError(r):
            print("stream error", r); sys.exit(1)
        f.write(dst.raw[:OUT - out_sz.value])
        pos += in_sz.value
        if r == 0:
            break
lib.ZSTD_freeDStream(dctx)
print(f"OK: decompressed to {sys.argv[2]}")
