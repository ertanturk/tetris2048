#!/usr/bin/env python3
"""Cross-platform PyInstaller build helper for the tetris2048 project.

This script wraps common PyInstaller invocations and adds convenience features.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from collections.abc import Sequence


# Removed unused `numpy._core.log` import; it was unused in this script.

# Project layout assumptions (script lives in tetris2048/build_scripts)
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
SRC_ENTRY = PROJECT_ROOT / "src" / "tetris2048" / "__main__.py"
DEFAULT_IMAGE_DIR = PROJECT_ROOT / "images"
logger = logging.getLogger(__name__)


def run_command(
	cmd: list[str], *, cwd: Path | None = None, shell: bool = False
) -> None:
	"""Run a subprocess and raise a descriptive error on failure."""
	msg = f"Running: {' '.join(cmd) if not shell else cmd}"
	logger.debug(msg)
	try:
		subprocess.run(cmd, check=True, cwd=(cwd or PROJECT_ROOT), shell=shell)  # noqa: S603
	except subprocess.CalledProcessError as exc:
		msg = f"Command failed (exit {exc.returncode}): {cmd}"
		raise RuntimeError(msg) from exc


def ensure_pyinstaller(install_cmd: str | None) -> None:
	"""Ensure PyInstaller is importable.

	If not, attempt to install via custom command or pip.
	"""
	try:
		import PyInstaller  # noqa: F401, PLC0415
	except ImportError:
		logger.warning(
			"PyInstaller is not installed in the current environment."
		)
	else:
		logger.debug("PyInstaller already installed.")
		return

	if install_cmd:
		msg = f"Attempting to install PyInstaller via command: {install_cmd}"
		logger.info(msg)
		try:
			run_command([install_cmd], shell=True)  # noqa: S604
		except RuntimeError as exc:
			msg = f"Install command failed: {exc}"
			logger.exception(msg)
			logger.info("Falling back to pip install of packaging extras.")

	logger.info(
		"Installing packaging extras via pip (this will install PyInstaller)."
	)
	run_command([sys.executable, "-m", "pip", "install", ".[packaging]"])


@dataclass
class BuildOptions:
	"""Options for PyInstaller build."""

	name: str
	onefile: bool
	windowed: bool
	icon: Path | None
	extra_add_data: list[str]
	hidden_imports: list[str]
	distpath: Path | None
	workpath: Path | None
	clean: bool
	noconfirm: bool
	spec_only: bool


def _get_add_data_args(extra_add_data: list[str]) -> list[str]:
	"""Construct add-data arguments for PyInstaller."""
	args: list[str] = []
	if DEFAULT_IMAGE_DIR.exists():
		args.append(f"{DEFAULT_IMAGE_DIR}{os.pathsep}images")
	else:
		logger.warning(
			"Warning: images directory not found; skipping automatic images bundling"  # noqa: E501
		)

	for spec in extra_add_data:
		# Normalize separators for cross-platform compatibility
		norm_spec = spec.replace(":", os.pathsep).replace(";", os.pathsep)
		if os.pathsep in norm_spec:
			parts = norm_spec.split(os.pathsep, 1)
			args.append(f"{parts[0]}{os.pathsep}{parts[1]}")
		else:
			args.append(f"{spec}{os.pathsep}{Path(spec).name}")
	return args


def _add_config_args(cmd: list[str], options: BuildOptions) -> None:
	"""Add core configuration flags and paths to the command list."""
	# Process boolean flags
	for flag, active in [
		("--clean", options.clean),
		("--noconfirm", options.noconfirm),
	]:
		if active:
			cmd.append(flag)

	# Process path arguments
	for flag, path in [
		("--distpath", options.distpath),
		("--workpath", options.workpath),
	]:
		if path:
			cmd += [flag, str(path)]

	# Name and execution mode
	cmd += ["--name", options.name]
	cmd.append("--onefile" if options.onefile else "--onedir")
	cmd.append("--windowed" if options.windowed else "--console")


def _add_resource_args(cmd: list[str], options: BuildOptions) -> None:
	"""Add resources and bundle all Tcl/Tk 9.0 binaries from uv."""
	if options.icon and options.icon.exists():
		cmd += ["--icon", str(options.icon)]
	elif options.icon:
		logger.warning("Warning: icon file not found: %s", options.icon)

	cmd += ["--collect-all", "tkinter"]
	cmd += ["--collect-all", "_tkinter"]

	uv_lib_path = Path(
		"/home/ertan/.local/share/uv/python/cpython-3.14.3-linux-x86_64-gnu/lib"
	)

	if uv_lib_path.exists():
		# Find and add all Tcl/Tk 9.0 related libraries
		for lib in uv_lib_path.glob("libtcl*9.0.so"):
			cmd += ["--add-binary", f"{lib}:."]
			logger.info("Bundling binary: %s", lib)
		for lib in uv_lib_path.glob("libtk*9.0.so"):
			cmd += ["--add-binary", f"{lib}:."]
			logger.info("Bundling binary: %s", lib)
	else:
		logger.error("Build failed: uv library path not found: %s", uv_lib_path)

	for data in _get_add_data_args(options.extra_add_data):
		cmd += ["--add-data", data]

	cmd += ["--hidden-import", "pygame"]
	if options.spec_only:
		cmd += ["--specpath", str(PROJECT_ROOT)]


def build_pyinstaller(options: BuildOptions) -> None:
	"""Run PyInstaller to build the project using BuildOptions."""
	if not SRC_ENTRY.exists():
		msg = f"Entry script not found: {SRC_ENTRY}"
		raise FileNotFoundError(msg)

	cmd = [sys.executable, "-m", "PyInstaller"]
	_add_config_args(cmd, options)
	_add_resource_args(cmd, options)
	cmd.append(str(SRC_ENTRY))

	logger.info("PyInstaller command: %s", " ".join(cmd))
	run_command(cmd)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
	"""Parse command line arguments."""
	p = argparse.ArgumentParser(description="Build standalone executables.")
	p.add_argument("--name", default="tetris2048", help="Artifact name")
	p.add_argument(
		"--onefile",
		action="store_true",
		default=True,
		help="Single-file output",
	)
	p.add_argument(
		"--onedir",
		dest="onefile",
		action="store_false",
		help="Directory output",
	)
	p.add_argument("--windowed", action="store_true", help="No console window")
	p.add_argument("--icon", type=Path, help="Path to icon file")
	p.add_argument(
		"--add-data", action="append", default=[], help="Format SRC:DEST"
	)
	p.add_argument(
		"--hidden-import",
		action="append",
		default=["pygame"],
		help="Hidden imports",
	)
	p.add_argument("--distpath", type=Path, help="Output directory")
	p.add_argument("--workpath", type=Path, help="Work directory")
	p.add_argument("--clean", action="store_true", help="Clean before build")
	p.add_argument(
		"--noconfirm", action="store_true", help="Overwrite without asking"
	)
	p.add_argument("--install-cmd", help="Custom install command")
	p.add_argument("--spec-only", action="store_true", help="Generate .spec only")
	p.add_argument(
		"--no-install-check", action="store_true", help="Skip PyInstaller check"
	)
	return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
	"""Main entry point."""
	args = parse_args(argv)

	if not args.no_install_check:
		try:
			ensure_pyinstaller(args.install_cmd)
		except (RuntimeError, FileNotFoundError) as exc:
			msg = f"Failed to ensure PyInstaller: {exc}"
			logger.exception(msg)
			return 2

	try:
		opts = BuildOptions(
			name=args.name,
			onefile=args.onefile,
			windowed=args.windowed,
			icon=args.icon,
			extra_add_data=args.add_data,
			hidden_imports=args.hidden_import,
			distpath=args.distpath,
			workpath=args.workpath,
			clean=args.clean,
			noconfirm=args.noconfirm,
			spec_only=args.spec_only,
		)
		build_pyinstaller(opts)
	except (RuntimeError, FileNotFoundError) as exc:
		msg = f"Build failed: {exc}"
		logger.exception(msg)
		return 1

	logger.info("Build completed successfully.")
	return 0


if __name__ == "__main__":
	sys.exit(main())
