
function deploy_drupal8() {
	WORKDIR=$(mktemp -d)
	cd $WORKDIR
	local PROJ="project/drupal/releases"
	local REL=$(curl https://www.drupal.org/$PROJ/ 2> /dev/null | egrep '<h2><a href="/'$PROJ'/8\.[0-9]+\.[0-9]+">' | awk -F\" 'NR==1 {print $2}')
	local VER=${REL##*/}

	curl -O https://ftp.drupal.org/files/projects/drupal-${VER}.tar.gz
	tar xf drupal-${VER}.tar.gz
	mv drupal-${VER}/* drupal-${VER}/.[^.]* $KUSANAGI_DIR/DocumentRoot
	cd $KUSANAGI_DIR/DocumentRoot

	rm -rf $WORKDIR

	cp sites/default/default.settings.php sites/default/settings.php
	chown -R kusanagi:www sites/default/
	chmod -R g+w sites/default/

	# create after_install shell script
	cat > $KUSANAGI_DIR/after_install.sh <<EOF
#!

chmod -R g-w $KUSANAGI_DIR/DocumentRoot/sites
chmod -R g-w $KUSANAGI_DIR/DocumentRoot/sites/default/
cat >> $KUSANAGI_DIR/DocumentRoot/sites/default/settings.php <<EOL

\\\$settings['trusted_host_patterns'] = array(
    '^${FQDN//\./\\.}\$',
    '^localhost\$',
);
EOL
EOF

	chmod 700 $KUSANAGI_DIR/after_install.sh

	# msg
	echo
	echo $(eval_gettext "Please access http://\$FQDN/ and install Drupal.")
	echo $(eval_gettext "After the installation of Drupal, please run the script(\$KUSANAGI_DIR/after_install.sh).")
}

deploy_drupal8
