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
from csorchestrator.application.recipes.repos_config import (
    RepoRefBuildPublishConfig,
    RepoRefBuildPublishConfigDict,
)
from csorchestrator.foundation.core.report import Report
from csorchestrator.frontend.cscmake_presets.supported_variants import (
    BuildConfig,
)
from csorchestrator.portable.release_manifest import PublishPackageMode


def create_orchestrator() -> OptionalOrchestratorWithReport:
    report = Report()

    base_target_dir = Path("workspace")
    base_install_dir = base_target_dir / Path("install")
    common_repo_ref = "dev"

    repos: RepoRefBuildPublishConfigDict = {
        "csCMake": RepoRefBuildPublishConfig(common_repo_ref, None),
        "eigen3": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "fmt": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.DEBUG_RELEASE),
        "fmt-eigen": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "cpptrace": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.DEBUG_RELEASE),
        "magic_enum": RepoRefBuildPublishConfig(
            common_repo_ref, BuildConfig.DEBUG_RELEASE, PublishPackageMode.HEADERS_ONLY
        ),
        "libassert": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.DEBUG_RELEASE),
        "tclap": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "Catch2": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.DEBUG_RELEASE),
        "pipes": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "NamedType": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-optional": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
        "tl-expected": RepoRefBuildPublishConfig(common_repo_ref, BuildConfig.RELEASE, PublishPackageMode.HEADERS_ONLY),
    }

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
        repo_access_token="${{ secrets.ACTIONS_ORG_ACCESS }}",
    )

    return OptionalOrchestratorWithReport.create_result_and_report(o, report)


def main(argv: Sequence[str] | None = None) -> int:
    script_path = str(Path(__file__).resolve())
    return orchestrator_main_with_default_run(script_path, argv)


if __name__ == "__main__":
    sys.exit(main())
