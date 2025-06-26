#!/usr/bin/env python3
"""TypeScript environment initializer for offline sandbox.

Installs vendored NPM tarballs located in *scripts/typescript/npm-packages/* into
``<repo>/.node_deps`` so that Node.js tooling (tsc, ts-node, tsx, mocha, etc.)
can run without network access.

This script is **idempotent** – if TypeScript is already available in
``.node_deps`` the installation step is skipped.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import importlib.util
import shutil
import urllib.request
import zipfile
import platform
import os
import tarfile
import json

if len(sys.argv) > 1:
    _repo_root = Path(sys.argv[1]).resolve()
else:
    _repo_root = Path(__file__).resolve().parent.parent.parent

_packages_dir = Path(__file__).resolve().parent / "npm-packages"
_cache_dir = _repo_root / ".node_deps"

NODEJS_VERSION = "20.12.2"  # LTS as of June 2024
NODEJS_BASE_URLS = {
    "windows": f"https://nodejs.org/dist/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-win-x64.zip",
    "darwin": f"https://nodejs.org/dist/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-darwin-x64.tar.gz",
    "linux": f"https://nodejs.org/dist/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-linux-x64.tar.xz",
}
NODEJS_LOCAL_DIR = Path(__file__).resolve().parent / "nodejs"
NODEJS_ARCHIVE_PATHS = {
    "windows": NODEJS_LOCAL_DIR / "node.zip",
    "darwin": NODEJS_LOCAL_DIR / "node.tar.gz",
    "linux": NODEJS_LOCAL_DIR / "node.tar.xz",
}


def _already_installed() -> bool:
    return (_cache_dir / "node_modules" / "typescript").exists()


def ensure_local_nodejs():
    """Download and extract Node.js for the current OS if not already present."""
    sys_platform = platform.system().lower()
    if sys_platform.startswith("win"):
        os_key = "windows"
        node_dirname = f"node-v{NODEJS_VERSION}-win-x64"
    elif sys_platform == "darwin":
        os_key = "darwin"
        node_dirname = f"node-v{NODEJS_VERSION}-darwin-x64"
    elif sys_platform == "linux":
        os_key = "linux"
        node_dirname = f"node-v{NODEJS_VERSION}-linux-x64"
    else:
        raise RuntimeError(f"Unsupported OS for Node.js bootstrapping: {sys_platform}")

    node_dir = NODEJS_LOCAL_DIR / node_dirname
    if node_dir.exists():
        return node_dir
    print(f"[typescript-initializer] Downloading Node.js v{NODEJS_VERSION} for {os_key}…")
    NODEJS_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    url = NODEJS_BASE_URLS[os_key]
    archive_path = NODEJS_ARCHIVE_PATHS[os_key]
    urllib.request.urlretrieve(url, archive_path)
    if os_key == "windows":
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(NODEJS_LOCAL_DIR)
    else:
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(NODEJS_LOCAL_DIR)
    print(f"[typescript-initializer] Node.js extracted to {NODEJS_LOCAL_DIR}")
    return node_dir


def find_npm():
    # Try system npm
    npm_path = shutil.which("npm")
    if npm_path:
        return npm_path, None
    sys_platform = platform.system().lower()
    node_dir = ensure_local_nodejs()
    if sys_platform.startswith("win"):
        npm_path = node_dir / "npm.cmd"
        if not npm_path.exists():
            npm_path = node_dir / "node_modules" / "npm" / "bin" / "npm-cli.js"
            if npm_path.exists():
                return str(npm_path), str(node_dir / "node.exe")
        else:
            return str(npm_path), str(node_dir / "node.exe")
    else:
        npm_path = node_dir / "bin" / "npm"
        node_bin = node_dir / "bin" / "node"
        if npm_path.exists():
            return str(npm_path), str(node_bin)
        # fallback: npm may be in node_modules/npm/bin/npm-cli.js
        npm_cli = node_dir / "lib" / "node_modules" / "npm" / "bin" / "npm-cli.js"
        if npm_cli.exists():
            return str(npm_cli), str(node_bin)
    return None, None


def _run_npm_install() -> None:
    tarballs = sorted(_packages_dir.glob("*.tgz"))
    if not tarballs:
        print("[typescript-initializer] No .tgz packages found in npm-packages/.", file=sys.stderr)
        sys.exit(1)

    npm_path, node_path = find_npm()
    if not npm_path:
        # Fallback: manually extract .tgz archives into node_modules for fully offline environments.
        print("[typescript-initializer] 'npm' not found – falling back to manual extraction of tarballs…")
        node_modules_dir = _cache_dir / "node_modules"
        node_modules_dir.mkdir(parents=True, exist_ok=True)
        for tarball in sorted(_packages_dir.glob("*.tgz")):
            pkg_name = tarball.stem.split('-')[0]  # crude but works for bundled tarballs like chai-4.3.8.tgz
            target_dir = node_modules_dir / pkg_name
            if target_dir.exists():
                continue  # already extracted
            with tarfile.open(tarball, "r:gz") as tf:
                # NPM tarballs have package/ prefix – extract stripping it
                for member in tf.getmembers():
                    if member.name.startswith("package/"):
                        member.name = member.name[len("package/"):]  # type: ignore
                        tf.extract(member, target_dir)
        # Still copy tools and configs then return
        _copy_tools_to_project_root(_repo_root)
        _copy_config_templates_to_project_root(_repo_root)
        return

    cmd = [
        npm_path,
        "install",
        "--ignore-scripts",
        "--no-audit",
        "--no-fund",
        "--prefix",
        str(_cache_dir),
        *map(str, tarballs),
    ]
    env = os.environ.copy()
    if node_path:
        # Prepend local nodejs dir to PATH
        env["PATH"] = str(Path(node_path).parent) + os.pathsep + env.get("PATH", "")

    print(f"[typescript-initializer] Installing vendored packages using {npm_path}…")
    subprocess.run(cmd, check=True, env=env)
    print("[typescript-initializer] Installation complete.")


def _copy_tools_to_project_root(project_root: Path):
    """Copy all .js and .cjs tool scripts from scripts/typescript/tools/ to <project_root>/tools/."""
    tools_src = Path(__file__).resolve().parent / "tools"
    tools_dst = project_root / "tools"
    tools_dst.mkdir(exist_ok=True)
    for tool_file in tools_src.glob("*.js"):
        shutil.copy(tool_file, tools_dst / tool_file.name)
    for tool_file in tools_src.glob("*.cjs"):
        shutil.copy(tool_file, tools_dst / tool_file.name)


def _merge_package_json_with_template(project_root: Path):
    """Ensure chai and @types/chai are present in package.json, merging with template if needed."""
    package_dst = project_root / "package.json"
    package_src = Path(__file__).resolve().parent / "package.template.json"
    if not package_dst.exists():
        shutil.copy(package_src, package_dst)
        return
    # Merge dependencies
    with open(package_dst, "r", encoding="utf-8") as f:
        existing = json.load(f)
    with open(package_src, "r", encoding="utf-8") as f:
        template = json.load(f)
    existing_deps = existing.get("dependencies", {})
    template_deps = template.get("dependencies", {})
    # Add/overwrite template deps into existing deps
    merged_deps = {**existing_deps, **template_deps}
    existing["dependencies"] = merged_deps
    
    # Remove problematic fields that conflict with our tooling
    if "type" in existing:
        del existing["type"]  # Remove "type": "module" to ensure CommonJS compatibility
    
    # Ensure devDependencies from template are also merged
    existing_dev_deps = existing.get("devDependencies", {})
    template_dev_deps = template.get("devDependencies", {})
    merged_dev_deps = {**existing_dev_deps, **template_dev_deps}
    existing["devDependencies"] = merged_dev_deps
    
    with open(package_dst, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def _copy_npm_packages_to_project_root(project_root: Path):
    """Copy required .tgz files from scripts/typescript/npm-packages/ to <project_root>/npm-packages/."""
    npm_src = Path(__file__).resolve().parent / "npm-packages"
    npm_dst = project_root / "npm-packages"
    npm_dst.mkdir(exist_ok=True)
    for pkg in [
        "chai-4.3.8.tgz",
        "mocha-10.2.0.tgz",
        "types-chai-4.3.11.tgz",
        "types-mocha-10.0.6.tgz",
        "types-node-20.11.0.tgz"
    ]:
        shutil.copy(npm_src / pkg, npm_dst / pkg)


def _copy_config_templates_to_project_root(project_root: Path):
    """Copy tsconfig.template.json, ensure package.json is merged with template, and copy npm-packages."""
    tsconfig_src = Path(__file__).resolve().parent / "tsconfig.template.json"
    tsconfig_dst = project_root / "tsconfig.json"
    if not tsconfig_dst.exists():
        shutil.copy(tsconfig_src, tsconfig_dst)
    _merge_package_json_with_template(project_root)
    _copy_npm_packages_to_project_root(project_root)


def main() -> None:
    _cache_dir.mkdir(exist_ok=True)

    npm_path, node_path = find_npm()
    env = os.environ.copy()
    if node_path:
        env["PATH"] = str(Path(node_path).parent) + os.pathsep + env.get("PATH", "")

    if _already_installed():
        print("[typescript-initializer] TypeScript already installed – nothing to do.")
        # Still ensure tools and configs are copied to project root
        _copy_tools_to_project_root(_repo_root)
        _copy_config_templates_to_project_root(_repo_root)
        # Only run npm install if npm is available
        if npm_path:
            subprocess.run([npm_path, "install"], cwd=_repo_root, env=env)
        return

    _run_npm_install()
    _copy_tools_to_project_root(_repo_root)
    _copy_config_templates_to_project_root(_repo_root)
    # Only run npm install if npm is available
    if npm_path:
        subprocess.run([npm_path, "install"], cwd=_repo_root, env=env)


def ensure_typescript_deps() -> None:
    """Public helper to guarantee TypeScript tooling is ready (idempotent)."""
    main()


if __name__ == "__main__":
    main() 