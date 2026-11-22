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
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.cscmake_presets.supported_variants import (
    BuildConfig,
    get_context_list_linux,
    get_context_list_macos,
)
from csorchestrator.portable.release_manifest import PublishPackageMode


def create_orchestrator() -> OptionalOrchestratorWithReport:
    report = Report()

    base_target_dir = Path("workspace")
    base_install_dir = base_target_dir / Path("install")
    cscmake_version = "1.0.0-rc10"

    # every library by tag: the forks v<upstream>-cs.<n>, the copies of our own their semver (FORKS.md)
    repos: RepoRefBuildPublishConfigDict = {
        "eigen3": RepoRefBuildPublishConfig("v5.0.1-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "fmt": RepoRefBuildPublishConfig("v12.2.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "fmt-eigen": RepoRefBuildPublishConfig("v1.0.0-rc2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "cpptrace": RepoRefBuildPublishConfig("v1.0.4-cs.2", BuildConfig.DEBUG_RELEASE),
        "magic_enum": RepoRefBuildPublishConfig(
            "v0.9.8-cs.2", BuildConfig.DEBUG_RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "libassert": RepoRefBuildPublishConfig("v2.2.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "tclap": RepoRefBuildPublishConfig("v1.0.0-rc2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "Catch2": RepoRefBuildPublishConfig("v3.16.1-cs.2", BuildConfig.DEBUG_RELEASE),
        "NamedType": RepoRefBuildPublishConfig("v1.1.0-rc2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-optional": RepoRefBuildPublishConfig("v1.1.0-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-expected": RepoRefBuildPublishConfig("v1.3.1-cs.2", BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
    }

    # on top of the default matrix (Ubuntu 22.04 / 24.04, Windows 10): Ubuntu 26.04 (as 22.04 / 24.04) and macOS
    # (arm64, Apple Clang; Ninja Multi-Config and Xcode)
    additional_matrix = (
        get_context_list_linux("ubuntu26.04") + get_context_list_macos("macos15") + get_context_list_macos("macos26")
    )

    dependencies: dict[str, set[str]] = {
        "fmt-eigen": {"eigen3", "fmt"},
        "libassert": {"cpptrace"},
    }

    o = create_default_orchestrator_and_default_checkout_build_upload(
        name="third_party_base_libs",
        version="0.1.0",
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
