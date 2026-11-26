#!/usr/bin/env python3
import sys
from collections.abc import Sequence
from pathlib import Path

from csorchestrator.application.cli.cli import orchestrator_main_with_default_run
from csorchestrator.application.factory.factory import (
    OptionalOrchestratorWithReport,
)
from csorchestrator.application.recipes.create_orchestrator import (
    create_default_orchestrator_and_default_checkout_build_upload,
)
from csorchestrator.application.recipes.cscmake_release import create_cscmake_release_archive
from csorchestrator.application.recipes.repos_config import (
    RepoRefBuildPublishConfig,
    RepoRefBuildPublishConfigDict,
)
from csorchestrator.domain.orchestrator.workflow_config import Cron, DayOfWeek
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.cscmake_presets.supported_variants import (
    BuildConfig,
    get_context_list_linux,
    get_context_list_macos,
)
from csorchestrator.portable.release_manifest import PublishPackageMode


def create_orchestrator() -> OptionalOrchestratorWithReport:
    report = Report()

    base_target_dir = Path("_csw")
    base_install_dir = base_target_dir / Path("install")
    cscmake_version = "1.1.0"

    # every library by tag: the forks v<upstream>-cs.<n>, the copies of our own their semver (README.md)
    repos: RepoRefBuildPublishConfigDict = {
        "eigen3": RepoRefBuildPublishConfig("v5.0.1-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "fmt": RepoRefBuildPublishConfig("v12.2.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "fmt-eigen": RepoRefBuildPublishConfig("v1.0.0", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "zstd": RepoRefBuildPublishConfig("v1.6.0-cs.1", BuildConfig.DEBUG_RELEASE),
        "cpptrace": RepoRefBuildPublishConfig("v1.0.4-cs.3", BuildConfig.DEBUG_RELEASE),
        "magic_enum": RepoRefBuildPublishConfig(
            "v0.10.0-cs.1", BuildConfig.DEBUG_RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "libassert": RepoRefBuildPublishConfig("v2.2.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "tclap": RepoRefBuildPublishConfig("v1.0.0", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "Catch2": RepoRefBuildPublishConfig("v3.16.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "NamedType": RepoRefBuildPublishConfig("v1.1.0", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-optional": RepoRefBuildPublishConfig("v1.1.0-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-expected": RepoRefBuildPublishConfig("v1.3.1-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "nlohmann_json": RepoRefBuildPublishConfig(
            "v3.12.0-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "tomlplusplus": RepoRefBuildPublishConfig("v3.5.1-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "CLI11": RepoRefBuildPublishConfig("v2.7.2-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "concurrentqueue": RepoRefBuildPublishConfig(
            "v1.0.5-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "unordered_dense": RepoRefBuildPublishConfig(
            "v5.3.3-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "nanobench": RepoRefBuildPublishConfig("v4.6.0-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "spdlog": RepoRefBuildPublishConfig("v1.17.0-cs.1", BuildConfig.DEBUG_RELEASE),
        "tracy": RepoRefBuildPublishConfig("v0.15.0-cs.1", BuildConfig.DEBUG_RELEASE),
        "nanobind": RepoRefBuildPublishConfig("v3.1.0-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "stb": RepoRefBuildPublishConfig("v1.0.0", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "bitsery": RepoRefBuildPublishConfig("v5.2.5-cs.1", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
    }

    # on top of the default matrix (Ubuntu 22.04 / 24.04, Windows 10): Ubuntu 26.04 (as 22.04 / 24.04) and macOS
    # (arm64, Apple Clang; Ninja Multi-Config and Xcode)
    additional_matrix = (
        get_context_list_linux("ubuntu26.04") + get_context_list_macos("macos15") + get_context_list_macos("macos26")
    )

    dependencies: dict[str, set[str]] = {
        "fmt-eigen": {"eigen3", "fmt"},
        "libassert": {"cpptrace"},
        "cpptrace": {"zstd"},
        "spdlog": {"fmt"},
        "CLI11": {"Catch2"},
    }

    o = create_default_orchestrator_and_default_checkout_build_upload(
        name="third_party_base_libs",
        # staggered weekly run (UTC), one project at a time in the build-train order (no shared runners)
        schedule=Cron.weekly(DayOfWeek.MON, hour=0, minute=15),
        version="0.1.1",
        base_target_dir=base_target_dir,
        base_install_dir=base_install_dir,
        repo_ref_build_publish_config_dict=repos,
        additional_files_list=[
            Path("third_party_base_libs_config.py"),
        ],
        repo_dependencies_dict=dependencies,
        repo_dependencies_dev_dict={},
        additional_matrix_list=additional_matrix,
        release_archive_list=[create_cscmake_release_archive(cscmake_version)],
    )

    return OptionalOrchestratorWithReport.create_result_and_report(o, report)


def main(argv: Sequence[str] | None = None) -> int:
    script_path = str(Path(__file__).resolve())
    return orchestrator_main_with_default_run(script_path, argv)


if __name__ == "__main__":
    sys.exit(main())
