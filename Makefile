# Sururu Linux — atalhos de build
# Rode num Debian 13: make deps && make build && make test

INC := config/includes.chroot


.PHONY: tamanho
.PHONY: deps prepare config build test clean checksum arte pngs docs site central

deps:
	sudo apt install -y live-build qemu-system-x86 xorriso python3

# Mostra o tamanho da ISO (o GitHub aceita até 2048 MB por arquivo)
tamanho:
	@ls -lh sururu-isaac-*.hybrid.iso && du -m sururu-isaac-*.hybrid.iso | awk '{ if ($$1 >= 2048) print "ATENÇÃO: passou de 2048 MB"; else print "OK: abaixo de 2048 MB" }'

arte:
	python3 artwork/gerar-wallpapers.py
	python3 artwork/gerar-boot.py

# Só para quem muda a arte de boot (precisa do Playwright): gera os PNGs
pngs: arte
	python3 scripts/renderizar-arte.py

# Copia arte, Central e padrões do desktop para dentro da imagem
prepare: arte
	install -d $(INC)/usr/share/sururu/wallpaper $(INC)/usr/share/sururu/central \
	  $(INC)/usr/share/icons/hicolor/scalable/apps $(INC)/usr/share/pixmaps \
	  $(INC)/usr/bin $(INC)/usr/share/applications $(INC)/etc/xdg/autostart \
	  $(INC)/etc/xdg/xfce4/xfconf/xfce-perchannel-xml $(INC)/etc/xdg/xfce4/panel \
	  $(INC)/etc/lightdm/lightdm-gtk-greeter.conf.d \
	  $(INC)/usr/share/plymouth/themes/sururu $(INC)/usr/share/sururu/boot $(INC)/etc/default/grub.d \
	  $(INC)/usr/share/sururu/calamares $(INC)/etc/skel
	cp artwork/wallpaper/*.png artwork/wallpaper/*.svg $(INC)/usr/share/sururu/wallpaper/
	cp artwork/sururu-simbolo.svg $(INC)/usr/share/icons/hicolor/scalable/apps/sururu.svg
	cp artwork/sururu-simbolo.svg $(INC)/usr/share/pixmaps/sururu.svg
	rm -rf $(INC)/usr/share/sururu/central && cp -r central $(INC)/usr/share/sururu/central
	find $(INC)/usr/share/sururu/central -name __pycache__ -prune -exec rm -rf {} +
	install -m 0755 packaging/bin/* $(INC)/usr/bin/
	cp packaging/applications/*.desktop $(INC)/usr/share/applications/
	cp packaging/xdg/autostart/*.desktop $(INC)/etc/xdg/autostart/
	cp packaging/xdg/xfce4/xfconf/xfce-perchannel-xml/*.xml $(INC)/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/
	cp packaging/xdg/xfce4/panel/default.xml $(INC)/etc/xdg/xfce4/panel/
	cp packaging/lightdm/50-sururu.conf $(INC)/etc/lightdm/lightdm-gtk-greeter.conf.d/
	cp packaging/plymouth/sururu/* $(INC)/usr/share/plymouth/themes/sururu/
	cp artwork/boot/plymouth-*.png $(INC)/usr/share/plymouth/themes/sururu/
	cp artwork/boot/splash-*.png $(INC)/usr/share/sururu/boot/
	cp packaging/grub/sururu.cfg $(INC)/etc/default/grub.d/
	cp packaging/calamares/show.qml $(INC)/usr/share/sururu/calamares/
	cp artwork/boot/plymouth-logo.png $(INC)/usr/share/sururu/boot/sururu-avatar.png
	cp artwork/boot/plymouth-logo.png $(INC)/etc/skel/.face
	./scripts/tema-boot.sh

config:
	sudo lb clean
	lb config

build: prepare config
	sudo lb build 2>&1 | tee build.log

test:
	./scripts/test-qemu.sh

# Roda a Central aqui mesmo, sem gerar ISO (bom para desenvolver)
central:
	python3 central/sururu_central.py

docs:
	pip install --break-system-packages -q mkdocs-material && mkdocs serve

# Monta o site completo (página + documentação) em ./publico, igual ao GitHub
site:
	rm -rf publico && mkdir -p publico && cp -r pagina/* publico/ && mkdocs build -d publico/docs
	@echo "Abra publico/index.html no navegador"

checksum:
	sha256sum sururu-isaac-*.hybrid.iso > SHA256SUMS

clean:
	sudo lb clean --purge
