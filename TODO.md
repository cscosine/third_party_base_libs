# TODO: next steps for third_party_base_libs

State (2026-11-16): every library at its latest upstream release, built with csCMake 1.0.0-rc6 (the released package,
`cscmake_version` in [`third_party_base_libs_project.py`](third_party_base_libs_project.py)) on 20 variants (Ubuntu
22.04 / 24.04 / 26.04, Windows, macOS 15 / 26); release `v0.1.0-rc8`. macOS: the compiled libraries (fmt, cpptrace,
libassert, Catch2) are built for macOS 13.3 and record it in their package (`share/cscmake/`), set in the
`cscmake-project-setup-macos` preset of their `csCMakeProjectSetup.json`; the header-only ones set nothing. Each work
stream ends with a new rc tag and a check of the consumers (csfoundation first).

## 1. Review the libraries: sync with upstream (one shot, then periodic)

Every library is a fork on `cscosine/<repo>` (`dev`) with our commits on top of an upstream commit. Our commits are
mostly the csCMake integration (`CMakePresets.json`, `csCMakeProjectSetup.json`, presets of the CI) and compiler fixes
(MSVC 2026, clang-cl); `fmt-eigen` and `tclap` use the `cs_*` commands.

| Library | Version shipped | Upstream (to confirm) | Last upstream commit in the fork | Our commits |
|---|---|---|---|---|
| eigen3 | 3.4.0 | gitlab.com/libeigen/eigen | none: the 3.4.0 archive downloaded at configure (`eigen-3.4.0/`, gitignored) | 38 |
| fmt | 11.2.1 | fmtlib/fmt | 2025-08-10 | 15 |
| fmt-eigen | 1.0.0 | (author Yunfan REN) | 2024-11-24 | 17 |
| cpptrace | 0.8.3 | jeremy-rifkin/cpptrace | 2025-05-18 | 17 |
| libassert | 2.1.5 | jeremy-rifkin/libassert | 2025-05-28 | 16 |
| magic_enum | 0.9.7 | Neargye/magic_enum | 2024-11-14 | 15 |
| tclap | 1.0.0 | (author mes5k; SourceForge / GitHub mirror) | 2020-12-30 | 16 |
| Catch2 | 3.10.0 | catchorg/Catch2 | 2025-08-26 | 17 |
| pipes (dropped 2026-11-16) | 0.0.1 | joboccara/pipes | 2024-10-30 | 14 |
| NamedType | 1.1.0 | joboccara/NamedType | 2022-09-29 | 11 |
| tl-optional | 1.0.0 | TartanLlama/optional | 2023-02-24 | 10 |
| tl-expected | 1.2.0 | TartanLlama/expected | 2025-07-12 | 11 |

Per library:

- [x] Add the upstream as a remote, compare: new releases since our base, what changed (breaking changes, new
      requirements: C++ standard, CMake version). Done 2026-11-15 (1.1).
- [x] Decide the base: an upstream **release tag** where one exists, else the upstream head.
- [x] Re-apply our commits on top, drop the ones the upstream made useless (libassert: the clang
      `-Wgnu-zero-variadic-macro-arguments` fix is still needed with 2.2.1, adapted to its new macros). The old `dev`
      of each fork: tag `legacy-<old version>`.
- [x] Build (one host build), then CI; tag an rc of this project; test the consumers (csopencvcpu, csfoundation,
      csoptimization, csImgTracker, csSkiTracker).
- [ ] Our fixes that are not csCMake-specific (compiler fixes): offer them upstream as pull requests, so the fork
      shrinks to the integration.
- [x] eigen3: a real fork of gitlab.com/libeigen/eigen (5.0.1 + one commit: the csCMake presets, tests / BLAS /
      LAPACK / demos / docs off), instead of the 3.4.0 archive downloaded at configure.

Periodic: every few months (or before a release of the consumers), the "compare" step for every library; a short
log of the check (date, upstream version, decision) in this file or in the README.

### 1.1 Assessment (2026-11-15)

Upstream versions (latest release) against what we ship:

| Library | Shipped | Upstream latest | Note |
|---|---|---|---|
| eigen3 | 3.4.0 (2021) | 3.4.1 (2025-09), 5.0.1 (2025-11) | no 3.5: 5.x is the successor of 3.4 (C++14, API cleanups). 3.4.1: bug fixes, same API, the safe step. 5.0: try on a branch with csopencvcpu and csfoundation (OpenCV 5.0 already reads the version variables of the Eigen 5 package config) |
| fmt | 11.2.1 | 12.2.1 | major: check the consumers (csCore) and fmt-eigen |
| cpptrace | 0.8.3 | 1.0.4 | major |
| libassert | 2.1.5 | 2.2.1 | with cpptrace 1.x |
| magic_enum | 0.9.7 | 0.9.8 | |
| Catch2 | 3.10.0 | 3.16.1 | |
| tl-expected | 1.2.0 | 1.3.1 | |
| tl-optional | 1.0.0 | 1.1.0 | the fork is on the 1.1.0 commit (2023-02-24): the version of the package is wrong |
| NamedType | 1.1.0 | (last release 1.0.0, 2018) | master |
| pipes (dropped) | 0.0.1 | (no release) | master |
| fmt-eigen, tclap | 1.0.0 | (no release / SourceForge 1.2.x, 1.4 rc) | versions of our own |

Bundled and fetched dependencies:

- [x] **libassert ships its own cpptrace** (0.8.2, Release only, with libdwarf and zstd): `LIBASSERT_USE_EXTERNAL_CPPTRACE`
      is `OFF` (upstream default), so the libassert package installs `libcpptrace.a`, `libdwarf.a`, `libzstd.a` and
      their CMake packages next to the cpptrace package (0.8.3): two versions of cpptrace, and which one a consumer
      of both (csCore) gets depends on the order of the prefix path. Fix: `LIBASSERT_USE_EXTERNAL_CPPTRACE=ON` in the
      libassert fork (cpptrace from this project, a dependency of libassert in the build order), then libassert
      installs itself only. Done (libassert 2.2.1).
- cpptrace fetches libdwarf (v0.12.0) and zstd at configure (`FetchContent`, pinned tags) and installs them as
  static libraries in its package: fine (pinned), but it needs the network at configure; libdwarf links **zlib of the
  system** (`ZLIB::ZLIB`): the consumers of cpptrace / libassert need `zlib1g-dev` on Linux (macOS: system zlib;
  Windows: no libdwarf, `dbghelp`).
- Test-only copies, not shipped: fmt `test/gtest`, magic_enum `test/3rdparty/Catch2`; tl-optional / tl-expected tests
  use the Catch2 package (`find_package(Catch2 3)`). Keep as is.
- eigen3: the 3.4.0 archive downloaded at configure (gitlab.com): the network at configure, as cpptrace.

System dependencies of the packages (checked: link interfaces, shared libraries): all static or header-only, no
absolute path, no Homebrew; system libraries: `dl` (Linux), zlib (Linux, macOS, through libdwarf), `dbghelp`
(Windows). Nothing to change besides the zlib note.

## 2. Quality of what we build, and libraries to add

- [ ] Warnings of the builds: e.g. eigen3 (`cmake_minimum_required` < 3.10 deprecated, policies CMP0167 / CMP0146
      in its tests). Fix in the fork, or document why kept.
- [ ] Tests: which libraries run their tests in the workflow (`fmt-eigen` and `tclap`: "No tests were found", their
      samples are only built). Decide per library: upstream tests on, at least in one configuration.
- [ ] Header-only libraries: compile each installed header on its own (`cs_target_check_installed_headers` for the
      csCMake ones), so a missing include is found here and not in a consumer.
- [ ] Package versions: `fmt-eigen` 1.0.0, `tclap` 1.0.0 are not upstream versions (check where they
      come from; the manifest and the consumers' `find_package` see them).
- [ ] Licences: the licence of every library in its install folder and in the release bundle.
- [ ] Debug / paranoid configurations: which libraries are published in which configurations (`BuildConfig` per
      repository), and whether the consumers need more (e.g. sanitizers need the libraries built with them?).
- [ ] CI cost: time per job, cache of the builds.
- [ ] Libraries to evaluate, by need of the consumers (csfoundation, csImgTracker, csSkiTracker), not by habit.
      For each: is it needed, header-only or not, maintained, licence, cost in the matrix. Constraints: no Boost, no
      big libraries (Qt and OpenCV have their own projects); C++17 (the standard of the projects); a compiled library
      is one more build in every variant, a header-only one is cheap. Shortlist (2026-11-15), nothing decided:

      | Library | For | Note |
      |---|---|---|
      | spdlog | logging | on top of our fmt (`SPDLOG_FMT_EXTERNAL`); compiled or header-only |
      | CLI11 | command line | header-only; the maintained replacement of tclap |
      | nlohmann/json | JSON (configuration, metadata, test data) | header-only; glaze is faster but C++23 |
      | toml++ | configuration files edited by hand | header-only, C++17; one of JSON / TOML for configurations |
      | moodycamel::concurrentqueue | lock-free queues (camera / tracking pipelines) | header-only |
      | ankerl::unordered_dense | fast hash map | header-only, one file |
      | Tracy (client) | frame / real-time profiling (the tracker applications) | the viewer apart |
      | nanobench | micro-benchmarks | one header; lighter than Google Benchmark |
      | zpp_bits or bitsery | binary serialization (datasets, recordings) | header-only |
      | zstd or lz4 | compression (datasets, recordings) | zstd is already built in cpptrace, not as a package |
      | Microsoft GSL | `not_null`, `narrow`, contracts | overlaps libassert |
      | stb_image / stb_image_write | PNG / JPEG without OpenCV (small tools, tests) | single headers |

      Not: doctest (Catch2 is there), range-v3 (compile time; C++20 ranges), mp-units (C++20), date (C++20 chrono).
      If only three: spdlog, CLI11, nlohmann/json.

      The libraries we have, to review the same way: tclap (-> CLI11), tl-optional (`std::optional` in C++17: only for `optional<T&>` and the monadic functions),
      NamedType (fine, upstream almost frozen). Dropped: pipes (2026-11-16: no upstream release, unmaintained, no
      consumer but the csCore wrapper; a nice API idea, https://github.com/joboccara/pipes; C++20 ranges cover it).

## 3. New configurations: Ubuntu 26.04, macOS

Branch `feature/ubuntu26mac` (here, csorchestrator, eigen3, fmt; csCMake: no change, 1.0.0-rc1 already has every
variant). The matrix is the default one of csorchestrator (Ubuntu 22.04 / 24.04, Windows 10: 12 variants, unchanged
for the other projects) plus 8 opt-in variants of this project (`additional_matrix_list` in
[`third_party_base_libs_project.py`](third_party_base_libs_project.py)):

| Variant | Runner | Status |
|---|---|---|
| Ubuntu 26.04 x64, gcc / clang, Ninja Multi-Config | `ubuntu-26.04` | green, no library change |
| Ubuntu 26.04 arm64, gcc / clang, Ninja | `ubuntu-26.04-arm` | green, no library change |
| macOS 15 / 26 arm64, Apple Clang, Ninja Multi-Config | `macos-15` / `macos-26` | green (eigen3 fix) |
| macOS 15 / 26 arm64, Apple Clang, Xcode | `macos-15` / `macos-26` | green (eigen3 fix, fmt test fix) |

Changes in the libraries (`feature/ubuntu26mac` of the forks):

- eigen3: the 3.4.0 archive was downloaded only `if(LINUX)` / `elseif(WIN32)` (macOS failed); obsolete with the
  fork of Eigen 5.0.1.
- fmt: `format-impl-test` not registered with the Xcode generator. Upstream test bug: `format-impl-test.cc` redefines
  `FMT_ASSERT` to throw, the other sources of the same executable use the aborting one (ODR); Xcode links the
  aborting definition and `bigint_test.multiply` aborts in Debug. The library is not affected.

Remaining:

- [x] Merged into `dev` (section 4), rc tag, then the consumers on the new variants (they opt in with
      `additional_matrix_list`).
- [ ] fmt: offer the ODR fix of `format-impl-test` upstream (e.g. `test-assert.h` in every source of the test).
- [ ] Decide whether to drop 22.04 at some point; macOS 15 for as long as GitHub provides the runner.
- [ ] CI cost: 20 jobs; per job (first run): Xcode ~16 min, macOS Ninja Multi-Config ~10, Ubuntu 26.04 5-10.
      Reduce to one generator per macOS version if needed.
- [ ] csorchestrator: the drift test against csCMake `variants.json` (step 1 of
      `../csorchestrator/TODO-cscmake-alignment.md`), still to do.

### 3.1 Consumers: csqt6, csopencvcpu (same branch name)

The consumers name the mapping of a provider with a matrix of its own (`qt6_mapping`, `csopencvcpu_mapping`, by name
in `provider_mapping_function`); a provider not named: identity.
csorchestrator: `get_supported_os_version_list` keeps the default versions (csqt6 and csopencvcuda build their matrix
from it), `get_all_supported_os_version_list` lists every version.

- csqt6 (Qt 6.11.1): Ubuntu 26.04 x64/arm64 and macOS 15/26 arm64, Apple Clang, Ninja (Release, as Linux). Both macOS
  versions so the archives survive the retirement of `macos-15`; `qt6_mapping`: a macOS consumer of any generator
  uses the build of its macOS version. macOS phase: free disk (Android SDK, other Xcodes, simulators), then the Linux
  scripts. Green at the first run; per job: macOS 15 ~96 min, macOS 26 ~147, Ubuntu 26.04 83-167 (as 22/24).
  The macOS package links only system frameworks/libraries (412 Mach-O files checked).
  Dependency check of the Linux / Windows packages: the MySQL and PostgreSQL SQL drivers linked the client libraries of
  the runners (`libmysqlclient`, `libpq`): configured off (`-no-feature-sql-mysql -no-feature-sql-psql`).
- csopencvcpu (OpenCV 5.0): Ubuntu 26.04 (4 variants as 22/24) and macOS 15/26 Ninja Multi-Config only;
  `csopencvcpu_mapping`: an Xcode consumer uses the Ninja Multi-Config archives. No Homebrew: everything is built in
  (zlib, jpeg, png, tiff, webp, openjpeg) or a system framework (Accelerate, AVFoundation, Cocoa, GCD).
  Changes in the opencv fork (`feature/ubuntu26mac`):
  - macOS install RPATH `@loader_path` (the presets set `$ORIGIN`, Linux only);
  - KleidiCV with GCC >= 15 (Ubuntu 26.04 arm64): `.text.neon` "section type conflict" between a template member
    and a plain function: fixed in KleidiCV 26.09 ("Fix GCC 14+ Debug builds of Lucas-Kanade"), the version of
    upstream OpenCV 5.x (PR 30128): the fork moves to KleidiCV 26.09 as upstream (was a patch of `config.h.in`);
  - macOS: contrib `freetype` module off by default (it linked the Homebrew freetype/harfbuzz of the runner).
- [x] Merged (section 4): csopencvcpu on the rc of this project and a new `-cpu` tag of the opencv fork.
- [ ] csopencvcuda: not touched (CUDA on 26.04 / no CUDA on macOS); its matrix is unchanged.

### 3.2 First-party projects (csfoundation, csoptimization, csImgTracker, csSkiTracker)

macOS: Ninja Multi-Config and Xcode (macOS 15 and 26), every project green with its smoke run. Deployment target 13.3 for every csCMake project (csCMake `cs-host-macos`: the floating-point
`std::to_chars` of `std::format` in the libc++ of Apple; Qt 6.11 needs 13.0, csqt6 keeps 13.0).

Fixes made on the way (`feature/ubuntu26mac` of each repository):

- pipes: `operator.hpp` without `<algorithm>` / `<iterator>` (libc++ of Apple); pipes dropped since.
- csVisOpenGL: macOS gets a 4.1 core profile context, the shaders the `#version` of the context (330 core; 130 on
  Linux / Windows as before): GLSL 1.30 does not exist on macOS, the sample crashed. The sample: a deployment and
  `--smoke`, run by csfoundation CI from its archive (the closing check: OpenGL 4.1 on macOS, 4.5 elsewhere).
- csBlockMatrix: `SparseCoeffDiagonalMatrixBlock`: `outerSize()` was in its `InnerIterator` (GCC 15 / recent Clang
  check the template bodies).
- csNelson, csBlockMatrix: OpenMP through csCore (`CS_OMP(...)`, only with `_OPENMP`; 1 thread without), csCMake
  `cs_target_use_openmp` does nothing with Apple Clang: built serial on macOS, no flags in the projects.
- csCore: csAssert generates one header for every configuration, the levels are per-configuration compile definitions
  (the Xcode generator does not support sources varying by configuration; design in the Readme of csCore).

Open:

- [ ] OpenMP on macOS: csBlockMatrix and csNelson are built without OpenMP on macOS (serial: Apple Clang has no
      OpenMP runtime, no Homebrew). To decide with the refactoring of those libraries: libomp as a package of this
      project, a thread pool given by the caller, or no OpenMP at all (measure first: `OMP_NUM_THREADS=1` against the
      default on Linux).
- [ ] csVisOpenGL on macOS: a 4.1 core profile, lines 1 px wide and points not smoothed (`glLineWidth` > 1 and
      `GL_POINT_SMOOTH` do not exist in a core profile) until phase 2 of its `docs/evolution-assessment.md` (core
      profile everywhere, lines and points expanded in the shaders).

## 4. Stable `dev`: Ubuntu 26.04 + macOS, the library updates, pipes dropped (2026-11-16)

`feature/ubuntu26mac` (every repository) and `feature/update_libs` (here and the forks) re-applied as a few commits per
repository on `feature/stable-dev`, merged into `dev` in the order of the release chain, each with its CI green on
every config and an rc. Plan: `PLAN-stable-dev-ubuntu26mac-libs.md` (workspace).

- csorchestrator: the variants; the release files outside the artifacts folder (the bundle was uploaded twice); the
  recipes `add_gui_deployment_run` (the project's command and check: exit code, an assessor `module:function` of the
  output) and `add_gui_deployment_smoke_test_return_0` (xvfb on Linux, Mesa llvmpipe on Windows, the desktop on
  macOS). No `consumer_mapping`: the consumers name the mappings.
- csCMake 1.0.0-rc5: deployment target 13.3; `cs_deployment_qt_gui` (the Qt plugins of a GUI application, per
  system); `cs_target_use_openmp` does nothing with Apple Clang.
- Here: the variants; the libraries at their latest release (the forks); pipes dropped.
- csqt6: the configure options in one string; the system packages of its plugins (xcb) installed with its download.
- opencv fork / csopencvcpu: KleidiCV 26.09, `@loader_path`, freetype off on macOS; Eigen 5.
- csCore (csAssert as a template, `CS_OMP`, no pipes), csVisOpenGL, csBlockMatrix, csNelson; csfoundation,
  csoptimization, csImgTracker, csSkiTracker on the new variants with the helpers of csCMake / csorchestrator.
