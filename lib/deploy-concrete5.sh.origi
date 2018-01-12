DL_VER=$(curl 'https://repo.prime-strategy.co.jp/api.php?q=c5_dl_view' 2> /dev/null)
DL_URL="https://www.concrete5.org/download_file/-/view/$DL_VER/"

wget --no-check-certificate -q -O /dev/null --spider $DL_URL
ret=$?

if [ $ret -eq 0 ] ; then
	local WORKDIR=$(mktemp -d)
	cd $WORKDIR
	mkdir c5
	wget --no-check-certificate -O 'concrete5.zip' $DL_URL
	echo $(eval_gettext 'Extracting archive file...')
	echo
	unzip -q -d c5 ./concrete5.zip
	mv ./c5/concrete5* ./concrete5
	mv ./concrete5/* /home/kusanagi/$PROFILE/DocumentRoot
	rm -rf $WORKDIR
else
	echo $(eval_gettext "Cannot get concrete5.zip.")
	echo $(eval_gettext "Failed.")
fi

cd /home/kusanagi/$PROFILE/DocumentRoot
chown -R kusanagi.kusanagi /home/kusanagi/$PROFILE
chmod 0777 /home/kusanagi/$PROFILE/DocumentRoot/packages
chmod 0777 /home/kusanagi/$PROFILE/DocumentRoot/application/config
chmod 0777 /home/kusanagi/$PROFILE/DocumentRoot/application/files
