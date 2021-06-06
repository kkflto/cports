from cbuild.step import fetch, extract, patch, configure
from cbuild.step import build as buildm, install, prepkg, pkg as pkgsm
from cbuild.core import logger, dependencies, pkg as pkgm, paths, xbps

import os

def build(step, pkg, depmap):
    if pkg.pkgname in depmap:
        pkg.error(f"build-time dependency cycle encountered for {pkg.pkgname} (dependency of {pkg.origin.pkgname})")

    depmap[pkg.pkgname] = True

    # check and install dependencies
    dependencies.install(pkg, pkg.origin.pkgname, "pkg", depmap)

    # run up to the step we need
    fetch.invoke(pkg)
    if step == "fetch":
        return
    extract.invoke(pkg)
    if step == "extract":
        return
    patch.invoke(pkg)
    if step == "patch":
        return
    configure.invoke(pkg, step)
    if step == "configure":
        return
    buildm.invoke(pkg, step)
    if step == "build":
        return

    # invoke install for main package
    install.invoke(pkg, False)

    # handle subpackages
    for sp in pkg.subpkg_list:
        install.invoke(sp, True)

    # after subpackages are done, do the same for main package in subpkg mode
    install.invoke(pkg, True)

    for sp in pkg.subpkg_list:
        prepkg.invoke(sp)

    prepkg.invoke(pkg)

    if step == "install":
        return

    # clear list of preregistered packages
    rp = open(pkg.statedir / f"{pkg.pkgname}_register_pkg", "w")
    rp.close()

    # generate binary packages
    for sp in pkg.subpkg_list:
        pkgsm.invoke(sp, paths.repository())

    pkgsm.invoke(pkg, paths.repository())

    # register binary packages

    genrepos = {}

    with open(pkg.statedir / f"{pkg.pkgname}_register_pkg") as f:
        for ln in f:
            repo, pkgn = ln.split(":")
            if not repo in genrepos:
                pkgs = []
                genrepos[repo] = pkgs
            else:
                pkgs = genrepos[repo]
            pkgs.append(pkgn.strip())

    for repo in genrepos:
        logger.get().out(f"Registering new packages to {repo}...")
        if not xbps.register_pkgs(
            genrepos[repo], repo, pkg.rparent.force_mode
        ):
            logger.get().out_red(f"Registering packages failed.")
            raise Exception()

    # cleanup
    pkgm.remove_autodeps(pkg)
    pkgm.remove_pkg_wrksrc(pkg)
    pkgm.remove_pkg(pkg)
    pkgm.remove_pkg_statedir(pkg)
