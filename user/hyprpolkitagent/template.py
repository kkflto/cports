pkgname = "hyprpolkitagent"
pkgver = "0.1.2"
pkgrel = 0
build_style = "cmake"
configure_args = ["-DCMAKE_BUILD_TYPE:STRING=Release"]
hostmakedepends = ["cmake", "pkgconf", "ninja"]
makedepends = ["qt6-qtdeclarative-devel", "hyprutils-devel", "polkit-devel", "polkit-qt-1-devel"]
pkgdesc = "Polkit authentication agent written in QT/QML"
maintainer = "kkflt <kkflt@cyberdude.com>"
license = "BSD-3-Clause"
url = "https://github.com/hyprwm/hyprpolkitagent"
source = f"{url}/archive/v{pkgver}/hyprlang-v{pkgver}.tar.gz" 
sha256 = "2aa642a55aab000ac340c9209063a3068fda5b419ad83116f3c87532f06b0a79"

def post_install(self):
	self.install_license("LICENSE")
	self.uninstall("usr/lib/systemd")
