# KUSANAGI INIT
# 2015/07/21
# version 1.0.4

function k_init()
{
	# Option
	local OPT PRE_OPT= _PROV=1
	local OPT_TZ OPT_LANG OPT_KEY OPT_PASS OPT_PHRASE OPT_DDBPASS OPT_WEB OPT_PHP OPT_RUBY
	local TZ LANGUAGE KEYBOARD KUSANAGI_PASS KUSANAGI_DBPASS
	for OPT in "$@"
	do
		# skip 1st argment "setting"
		if [ $_PROV ] ; then
			_PROV=
		elif [ $OPT_TZ ] ; then
			if [ 1 -eq $(timedatectl list-timezones| grep -i $OPT| wc -l)  ] ; then
				TZ=$(timedatectl list-timezones| grep -i $OPT| tr -d '\r\n')
				OPT_TZ=
			else
				echo $(eval_gettext "option \$PRE_OPT \$OPT: illegal TZ String.")
				return 1
			fi
		elif [ $OPT_LANG ] ; then
			if [ "$OPT" = "ja" -o "$OPT" = "en" ] ; then
				LANGUAGE=$OPT
				OPT_LANG=
			else
				echo $(eval_gettext "option \$PRE_OPT \$OPT: please input 'en' or 'ja'.")
				return 1
			fi
		elif [ $OPT_KEY ] ; then
			if [ "$OPT" = "ja" -o "$OPT" = "en" ] ; then
				KEYBOARD=$OPT
				OPT_KEY=
			else
				echo $(eval_gettext "option \$PRE_OPT \$OPT: please input 'en' or 'ja'.")
				return 1
			fi
		elif [ $OPT_PASS ] ; then
			KUSANAGI_PASS=$OPT
			OPT_PASS=
		elif [ $OPT_PHRASE ] ; then
			if [[ ! $OPT =~ ^.{5,}$ ]]; then
				echo $(eval_gettext "option \$PRE_OPT \$OPT: please input 5 characters minimum.")
				return 1
			fi
			local KUSANAGI_PHRASE=$OPT
			OPT_PHRASE=
		elif [ $OPT_DBPASS ] ; then
			if [ 1 -eq $(check_db_root_password $OPT) ] ; then
				echo $(eval_gettext "option \$PRE_OPT \$OPT: please input [a-zA-Z0-9.!#%+_-] 8 characters minimum.")
				return 1
			fi
			KUSANAGI_DBPASS=$OPT
			OPT_DBPASS=
		else
			case "${OPT,,}" in
			'--tz')
				OPT_TZ=1
				;;
			'--lang')
				OPT_LANG=1
				;;
			'--keyboard')
				OPT_KEY=1
				;;
			'--passwd'|'--kusanagi-pass')
				OPT_PASS=1
				;;
			'--phrase'|'--kusanagi-phrase')
				OPT_PHRASE=1
				;;
			'--no-phrase'|'--nophrase')
				local KUSANAGI_PHRASE=''
				;;
			'--dbrootpass')
				OPT_DBPASS=1
				;;
			'--nginx')
				[ $OPT_WEB ] || OPT_WEB=nginx
				;;
			'--httpd')
				[ $OPT_WEB ] || OPT_WEB=httpd
				;;
			'--hhvm')
				[ $OPT_PHP ] || OPT_PHP=hhvm
				;;
			'--php7')
				[ $OPT_PHP ] || OPT_PHP=php7
				;;
			'--php5')
				[ $OPT_PHP ] || OPT_PHP=php5
				;;
			'--ruby24')
				[ $OPT_RUBY ] || OPT_RUBY=ruby24; kusanagi ruby24
				;;
			*)
				echo $(eval_gettext "Cannot use option \$OPT")
				return 1
				;;
			esac
		fi
		PRE_OPT=$OPT
	done

	echo

	# Check KUSANAGI version && update
	echo $(eval_gettext "Checking KUSANAGI Version.")

	local CUR_VER=$(yum list installed kusanagi | tail -n1 | sed 's/kusanagi.noarch *//g' | sed 's/ *@kusanagi//g')
	local CLOUD=$(cat /etc/kusanagi | tail -n1)
	local UA="KUSANAGI:$CLOUD;VersionChecker"
	local VC_URL="https://repo.prime-strategy.co.jp/api.php?q=version&p=kusanagi"
	local LAT_VER=$(wget -q -O - --user-agent="$UA" --no-cache --timeout=3 $VC_URL)
	k_ver_compare $LAT_VER $CUR_VER
	local RET=$?
	if [ 1 = $RET ]; then
		echo $(eval_gettext "KUSANAGI LAT_VER is avilable. Start update.") | sed "s|LAT_VER|$LAT_VAR|"
		yum --enablerepo=remi,remi-php56 update -y
	else
		echo $(eval_gettext "KUSANAGI is already latest version.")
	fi
	# generate security keys
	k_generate_seckey
	sleep 1s

	# Install Let's Encrypt tools
	if [ -e /usr/local/certbot/certbot-auto ]; then
		echo $(eval_gettext "Checking certbot-auto update.")
		/usr/local/certbot/certbot-auto --version --noninteractive > /dev/null
	fi

	## kusanagi machine timezone
	if [ -z "$TZ" ] ; then
		peco_dir=/etc/peco.d
		if [ ! -e $peco_dir ]; then
			mkdir -p $peco_dir
		fi
		if [ ! -e $peco_dir/config.json ]; then
			cp -p /usr/lib/kusanagi/resource$peco_dir/config.json $peco_dir/config.json
		fi

		TZ="$(timedatectl list-timezones | /usr/bin/peco --rcfile=/etc/peco.d/config.json --prompt 'Search or select timezone: ')"
		if [ -z "$TZ" ] ; then
			echo $(eval_gettext "Exiting.")
			return 1
		fi
		echo
	fi
	echo $(eval_gettext "Applying Location: DZS.") | sed "s|DZS|$TZ|"
	timedatectl set-timezone $TZ

	## kusanagi language select
	if [ -z "$LANGUAGE" ] ; then
		while :
		do
			echo -n "Select your using language.

1 : English
2 : 日本語

q : quit

Which are you using?: "
			read uselang
			case "$uselang" in
			"1" )
				echo
				echo $(eval_gettext "You choose: English")
				LANGUAGE="en"
				break
				;;
			"2" )
				echo
				echo $(eval_gettext "You choose: Japanese")
				LANGUAGE="ja"
				break
				;;
			"q" )
				echo
				echo $(eval_gettext "Exit.")
				return 1
				break
				;;
			* )
				;;
			esac
		done
	fi

	case "$LANGUAGE" in
	"en")
		localectl set-locale LANG=en_US.UTF-8
		;;
	"ja")
		localectl set-locale LANG=ja_JP.UTF-8
		;;
	*)
		;;
	esac

	## kusanagi keyboard select
	if [ -z "$KEYBOARD" ] ; then
		while :
		do
			echo $(eval_gettext "Select your keyboard layout.")
			echo
			echo $(eval_gettext "1 : English")
			echo $(eval_gettext "2 : Japanese")
			echo
			echo $(eval_gettext "q : quit")
			echo
			read usekey
			case "$usekey" in
			"1" )
				echo
				echo $(eval_gettext "You choose: English")
				break
				;;
			"2" )
				echo
				echo $(eval_gettext "You choose: Japanese")
				break
				;;
			"q" )
				echo
				echo $(eval_gettext "Exit.")
				return 1
				break
				;;
			* )
			;;
			esac
		done
	fi
	case "$KEYBOARD" in
	"en")
		localectl set-keymap us
		;;
	"ja")
		localectl set-keymap jp106
		;;
	*)
		;;
	esac

	## kusanagi user password
	local KUSER=`cat /etc/shadow | grep kusanagi`
	if [ -z "$KUSANAGI_PASS" ] ; then
		RET=""
		while [ "$RET" = "" ]; do
			echo $(eval_gettext "kusanagi user password using in software update.")
			echo

			passwd kusanagi
			RET=`cat /etc/shadow | grep kusanagi`
			if [ "$KUSER" = "$RET" ]; then
				RET=""
			fi
		done
	else
		echo $(eval_gettext "Set kusanagi user password using in software update.")
		expect -c "
			set timeout 1
			spawn passwd kusanagi
			expect Enter\ ; send \"$KUSANAGI_PASS\"; send \r
			expect Retype\ ; send \"$KUSANAGI_PASS\"; send \r
			expect eof exit 0" > /dev/null
	fi

	## kusanagi user ssh-keygen
	if [ -v KUSANAGI_PHRASE ] ; then
		echo $(eval_gettext "Generate kusanagi user ssh-key. use passprase(\"\$KUSANAGI_PHRASE\")")
		expect -c "
			set timeout 1
			spawn ssh-keygen -t rsa -f /root/kusanagi.pem
			expect \"Enter passphrase \"; send \"$KUSANAGI_PHRASE\" ; send \r
			expect \"Enter same passphrase \" ; send \"$KUSANAGI_PHRASE\" ; send \r
			expect eof exit 0" > /dev/null
	else
		RET=""
		while [ "$RET" = "" ]; do
			echo
			ssh-keygen -t rsa -f /root/kusanagi.pem

			if [ -e /root/kusanagi.pem ]; then
				RET="OK"
			fi
		done
	fi

	if [ -d /home/kusanagi/.ssh ]; then
		:				# do notiong
	else
		mkdir -p -m 700 /home/kusanagi/.ssh
		chown kusanagi:kusanagi /home/kusanagi/.ssh
	fi
	cat /root/kusanagi.pem.pub > /home/kusanagi/.ssh/authorized_keys
	rm /root/kusanagi.pem.pub

	RET=`find /root /home -name authorized_keys | grep -v kusanagi | head -1`
	if [ "$RET" != "" ]; then
		cat $RET >> /home/kusanagi/.ssh/authorized_keys
		if [[ $RET =~ ^(/home/([^/]*)/) ]]; then
			FILE=${BASH_REMATCH[1]}kusanagi.pem
			OWNER=${BASH_REMATCH[2]}
			mv /root/kusanagi.pem $FILE
			chown $OWNER:$OWNER $FILE
			echo $(eval_gettext "/root/kusanagi.pem.pub is moved to /home/kusanagi/.ssh/authorized_keys.")
			echo $(eval_gettext "RET is added to /home/kusanagi/.ssh/authorized_keys.") | sed "s|RET|$RET|"
			echo $(eval_gettext "/root/kusanagi.pem is moved to FILE.") | sed "s|FILE|$FILE|"
		fi
	fi

	## DB root password
	DB_ROOT_PASSWORD=`get_db_root_password`
	if [ "$DB_ROOT_PASSWORD" = "" ]; then
		echo $(eval_gettext "Can't get DB root password.")
		return 1
	fi

	if [ -z "$KUSANAGI_DBPASS" ] ; then
		RET=""
		while [ "$RET" = "" ]; do
			echo
			echo $(eval_gettext "Enter MySQL root password. Use [a-zA-Z0-9.!#%+_-] 8 characters minimum.")
			read -s PASS1
			echo $(eval_gettext "Re-type MySQL root password.")
			read -s PASS2
			if [ "$PASS1" = "$PASS2" ] && \
				[ 0 -eq $(check_db_root_password "$PASS1") ] ; then
				KUSANAGI_DBPASS="$PASS1"
				break
			fi
		done
	fi
	RET=$(set_db_root_password "$DB_ROOT_PASSWORD" "$KUSANAGI_DBPASS")
	echo $RET
	if [ "$RET" = "Failed." ]; then
		return 1
	fi
	echo $(eval_gettext "Change MySQL root password.")

	## configure web server
	if [ -z "$OPT_WEB" ] ; then
		echo
		while :
		do
			echo $(eval_gettext "KUSANAGI can choose middlewares.")
			echo $(eval_gettext "Please tell me your web server option.")
			echo $(eval_gettext "1) NGINX(Default)")
			echo $(eval_gettext "2) Apache")
			echo
			echo -n $(eval_gettext "Which you using?(1): " )
			read websrv
			case "$websrv" in
			""|"1" )
				echo
				echo $(eval_gettext "You choose: NGINX")
				OPT_WEB=nginx
				break
				;;
			"2" )
				echo
				echo $(eval_gettext "You choose: Apache")
				OPT_WEB=httpd
				break
				;;
			* )
				;;
			esac
		done
	fi
	case "$OPT_WEB" in
		'nginx')
			kusanagi nginx
			;;
		'httpd')
			kusanagi httpd
			;;
		*)
			;;
	esac

	## configure php
	if [ -z "$OPT_PHP" ] ; then
		while :
		do
			echo $(eval_gettext "Then, Please tell me your application server option.")
			echo $(eval_gettext "1) HHVM(Default)")
			echo $(eval_gettext "2) PHP7")
			echo $(eval_gettext "3) PHP5")
			echo
			echo -n $(eval_gettext "Which you using?(1): ")
			read websrv
			case "$websrv" in
			""|"1" )
				echo
				echo $(eval_gettext "You choose: HHVM")
				OPT_PHP=hhvm
   	   		 	break
				;;
			"2" )
				echo
				echo $(eval_gettext "You choose: PHP7")
				OPT_PHP=php7
				break
   	   	 	;;

			"3" )
				echo
				echo $(eval_gettext "You choose: PHP5")
				OPT_PHP=php5
				break
				;;

			* )
				;;
			esac
		done
	fi
	case "$OPT_PHP" in
	'hhvm')
		kusanagi hhvm
		;;
	'php7')
		kusanagi php7
		;;
	'php5')
		kusanagi php-fpm
		;;
	*)
		;;
	esac

	## configure ruby
	if [ -z "$OPT_RUBY" ] ; then
		k_ruby_init;
	fi

	k_configure
	k_monit monit on

	echo
	echo $(eval_gettext "KUSANAGI initialization completed")

	return 0
}
