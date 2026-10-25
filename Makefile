# Sururu Linux — atalhos de build
# Rode num Debian 13 (seu servidor k8s serve): sudo apt install live-build qemu-system-x86

.PHONY: deps config build test clean checksum

deps:
	sudo apt install -y live-build qemu-system-x86 xorriso

config:
	sudo lb clean
	lb config

build: config
	sudo lb build 2>&1 | tee build.log

test:
	./scripts/test-qemu.sh

checksum:
	sha256sum sururu-isaac-*.hybrid.iso > SHA256SUMS

clean:
	sudo lb clean --purge
