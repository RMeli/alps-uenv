# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Libunwind(AutotoolsPackage):
    """A portable and efficient C programming interface (API) to determine
    the call-chain of a program."""

    homepage = "https://www.nongnu.org/libunwind/"
    url = "https://github.com/libunwind/libunwind/releases/download/v0.0.0/libunwind-0.0.0.tar.gz"
    git = "https://github.com/libunwind/libunwind"
    maintainers("mwkrentel")

    license("MIT")

    version("master", branch="master")
    version("1.8-stable", branch="v1.8-stable")
    version("1.8.1", sha256="ddf0e32dd5fafe5283198d37e4bf9decf7ba1770b6e7e006c33e6df79e6a6157")
    version("1.7-stable", branch="v1.7-stable")
    version("1.7.2", sha256="a18a6a24307443a8ace7a8acc2ce79fbbe6826cd0edf98d6326d0225d6a5d6e6")
    version("1.6-stable", branch="v1.6-stable")
    version("1.6.2", sha256="4a6aec666991fb45d0889c44aede8ad6eb108071c3554fcdff671f9c94794976")
    version("1.5.0", sha256="90337653d92d4a13de590781371c604f9031cdb50520366aa1e3a91e1efb1017")
    version("1.4.0", sha256="df59c931bd4d7ebfd83ee481c943edf015138089b8e50abed8d9c57ba9338435")
    version("1.3.1", sha256="43997a3939b6ccdf2f669b50fdb8a4d3205374728c2923ddc2354c65260214f8")
    version("1.2.1", sha256="3f3ecb90e28cbe53fba7a4a27ccce7aad188d3210bb1964a923a731a27a75acb")

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    variant("docs", default=True, description="Build man page")
    variant(
        "libs",
        default="shared,static",
        values=("shared", "static"),
        multi=True,
        description="Build shared libs, static libs or both",
    )
    variant("pic", default=False, description="Compile with position independent code.")
    variant("tests", default=True, description="Build tests")

    variant(
        "block_signals",
        default=False,
        description="Block signals before performing mutex operations",
    )

    variant(
        "components",
        values=any_combination_of("coredump", "ptrace", "setjmp"),
        description="Build specified libunwind libraries",
    )

    variant(
        "conservative_checks",
        default=False,
        description="Validate all memory addresses before use",
    )

    variant("cxx_exceptions", default=False, description="Use libunwind to handle C++ exceptions")

    variant("debug", default=False, description="Turn on debug support (slows down execution)")

    variant(
        "debug_frame", default=False, description='Load the ".debug_frame" section if available'
    )

    variant("weak_backtrace", default=True, description="Provide the weak 'backtrace' symbol")

    variant("xz", default=False, description="Support xz (lzma) compressed symbol tables.")

    variant(
        "zlib",
        default=False,
        description="Support zlib compressed symbol tables " "(1.5 and later).",
    )

    # The libunwind releases contain the autotools generated files,
    # but the git repo snapshots do not.
    reconf_versions = "@master,1.6-stable,1.7-stable,1.8-stable"
    depends_on("autoconf", type="build", when=reconf_versions)
    depends_on("automake", type="build", when=reconf_versions)
    depends_on("libtool", type="build", when=reconf_versions)
    depends_on("m4", type="build", when=reconf_versions)

    depends_on("xz", type="link", when="+xz")
    depends_on("zlib-api", type="link", when="+zlib")

    conflicts("platform=darwin", msg="Non-GNU libunwind needs ELF libraries Darwin does not have")

    # Introduced in https://github.com/libunwind/libunwind/pull/555, fixed in
    # https://github.com/libunwind/libunwind/pull/723
    conflicts("target=ppc64:", when="@1.8")
    conflicts("target=ppc64le:", when="@1.8")

    conflicts("target=aarch64:", when="@1.8:")

    provides("unwind")

    def url_for_version(self, version):
        if version == Version("1.5.0"):
            return f"https://github.com/libunwind/libunwind/releases/download/v{version.up_to(2)}/libunwind-{version}.tar.gz"
        else:
            return super().url_for_version(version)

    def flag_handler(self, name, flags):
        wrapper_flags = []

        if name == "cflags":
            # https://github.com/libunwind/libunwind/pull/166
            if (
                self.spec.satisfies("@:1.4 %gcc@10:")
                or self.spec.satisfies("@:1.4 %cce@11:")
                or self.spec.satisfies("@:1.4 %clang@11:")
            ):
                wrapper_flags.append("-fcommon")

            if self.spec.satisfies("+pic"):
                wrapper_flags.append(self.compiler.cc_pic_flag)

        return (wrapper_flags, None, flags)

    def configure_args(self):
        spec = self.spec
        args = []

        args += self.enable_or_disable("documentation", variant="docs")
        args += self.enable_or_disable("libs")
        args += self.enable_or_disable("tests")

        args += self.enable_or_disable("block-signals", variant="block_signals")
        args += self.enable_or_disable("components")
        args += self.enable_or_disable("conservative-checks", variant="conservative_checks")
        args += self.enable_or_disable("cxx-exceptions", variant="cxx_exceptions")
        args += self.enable_or_disable("debug")
        args += self.enable_or_disable("debug-frame", variant="debug_frame")
        args += self.enable_or_disable("minidebuginfo", variant="xz")
        #  building without weak backtrace symbol is possible in 1.5.x and later
        if self.spec.satisfies("@1.5:"):
            args += self.enable_or_disable("weak-backtrace", variant="weak_backtrace")
        # zlib support is available in 1.5.x and later
        if spec.satisfies("@1.5:"):
            args += self.enable_or_disable("zlibdebuginfo", variant="zlib")

        return args
