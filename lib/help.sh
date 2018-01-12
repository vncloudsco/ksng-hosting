function helphelp {
	case $2 in
	'help'|'--help')
		case $1 in
			init)
				echo $(eval_gettext "Init: Initialization for use KUSANAGI.")
				echo "	"$(eval_gettext "Argument: [options]")
				echo "	"$(eval_gettext "Option: [--tz TZ]")
				echo "		"$(eval_gettext "Set Timezone to TZ.")
				echo "	"$(eval_gettext "Option: [--lang [ja|en]]")
				echo "		"$(eval_gettext "Set locale to ja or en.")
				echo "	"$(eval_gettext "Option: [--keyboard [ja|en]]")
				echo "		"$(eval_gettext "Set keyboard type to ja or en.")
				echo "	"$(eval_gettext "Option: [--passwd PASSWD]")
				echo "		"$(eval_gettext "Set kusanagi password to PASSWD.")
				echo "	"$(eval_gettext "Option: [--phrase PHRASE]")
				echo "		"$(eval_gettext "Set kusanagi ssh key's passphrase to PHRASE.")
				echo "	"$(eval_gettext "Option: [--no-phrase]")
				echo "		"$(eval_gettext "Set kusanagi ssh key's passphrase to null.")
				echo "	"$(eval_gettext "Option: [--dbrootpass DBPASS]")
				echo "		"$(eval_gettext "Set MySQL DB's root password to DBPASS.")
				echo "	"$(eval_gettext "Option: [--nginx|--httpd]")
				echo "		"$(eval_gettext "Set Web Service to nginx or httpd.")
				echo "	"$(eval_gettext "Option: [--hhvm|--php7|--php5]")
				echo "		"$(eval_gettext "Set PHP Service to hhvm, php7 or php5.")
				exit 0
				;;
			provision)
				echo $(eval_gettext "Provision: Provision profile(site).")
				echo "	"$(eval_gettext "Argument: [options] profile")
				echo "	"$(eval_gettext "Option: profile")
				echo "		"$(eval_gettext "Target profile name.")
				echo "	"$(eval_gettext "Option: --wordpress|--WordPress")
				echo "		"$(eval_gettext "Provision new profile to use WordPress.")
				echo "	"$(eval_gettext "Option: --woo|--WooCommerce")
				echo "		"$(eval_gettext "Provision WordPress with WooCommerce plugin.")
				echo "	"$(eval_gettext "Option: --lamp")
				echo "		"$(eval_gettext "Provision new profile to use LAMP.")
				echo "	"$(eval_gettext "Option: --c5|--concrete5")
				echo "		"$(eval_gettext "Provision new profile to use Concrete5.")
				echo "	"$(eval_gettext "Option: --drupal|--drupal8")
				echo "		"$(eval_gettext "Provision new profile to use Drupal8.")
				echo "	"$(eval_gettext "Option: --wplang [en_US|ja]")
				echo "		"$(eval_gettext "Set WordPress Language english(en_US) or Japanese(ja).")
				echo "		"$(eval_gettext "If do not specify it, use choose this parameter interactively.")
				echo "	"$(eval_gettext "Option: --fqdn domainname")
				echo "		"$(eval_gettext "Set host name to new domainname.")
				echo "	"$(eval_gettext "Option: --email mail_address")
				echo "		"$(eval_gettext "Set Email address to Let's Encrypt certiticates.")
				echo "		"$(eval_gettext "If do not specify --email and --no-email, use choose this parameter interactively.")
				echo "	"$(eval_gettext "Option: --no-email|--noemail")
				echo "		"$(eval_gettext "Unset Email address, and Do not execute Let's Encrypt certiticates.")
				echo "		"$(eval_gettext "If do not specify --email and --no-email, use choose this parameter interactively.")
				echo "	"$(eval_gettext "Option: --dbname name")
				echo "		"$(eval_gettext "Set MySQL Database name.")
				echo "		"$(eval_gettext "If do not specify it, use choose this parameter interactively.")
				echo "	"$(eval_gettext "Option: --dbuser user")
				echo "		"$(eval_gettext "Set MySQL Database user name.")
				echo "		"$(eval_gettext "If do not specify it, use choose this parameter interactively.")
				echo "	"$(eval_gettext "Option: --dbpass password")
				echo "		"$(eval_gettext "Set MySQL Database user's password.")
				echo "		"$(eval_gettext "If do not specify it, use choose this parameter interactively.")
				exit 0
				;;
			setting)
				echo $(eval_gettext "Setting: Change site URL to target profile.")
				echo "	"$(eval_gettext "Argument: --fqdn domainname [profile]")
				echo "	"$(eval_gettext "Option: --fqdn domainname")
				echo "		"$(eval_gettext "Change existing host name to domainname.")
				echo "	"$(eval_gettext "Option: [profile]")
				echo "		"$(eval_gettext "Target Profile name. If do not specify it, use the current profile.")
				exit 0
				;;
			ssl)
				echo $(eval_gettext "SSL: modify SSL Certificate configurations.")
				echo "	"$(eval_gettext "Option: --email email@example.com")
				echo "		"$(eval_gettext "Create new Let's Encrypt certificate to target profile.")
				echo "		"$(eval_gettext "Specified your E-Mail address(to use expire notice email,etc...)")
				echo "	"$(eval_gettext "Option: --cert certfile --key keyfile")
				echo "		"$(eval_gettext "Use specified certificate and key files.")
				echo "		"$(eval_gettext "These option cannot use with --email option.")
				echo "	"$(eval_gettext "Option: --https [redirect|noredirect]")
				echo "		"$(eval_gettext "Redirect or No Redirect HTTP to HTTPS site to target profile.")
				echo "	"$(eval_gettext "Option: --hsts [off|weak|mid|high]")
				echo "		"$(eval_gettext "use HSTS(HTTP Strict Transport Security) setting.")
				echo "		"$(eval_gettext "off:  Disable HSTS")
				echo "		"$(eval_gettext "weak: Enabling HSTS(not IncludeSubDomain)")
				echo "		"$(eval_gettext "mid:  Enabling HSTS w/IncludeSubDomain (not Preloading)")
				echo "		"$(eval_gettext "high: Enabling HSTS w/IncludeSubDomain,Preloading")
				echo "	"$(eval_gettext "Option: --auto [on|off]")
				echo "		"$(eval_gettext "Enable or disable auto renewal Let's Encrypt certification.")
				echo "	"$(eval_gettext "Option: --ct [on|off]")
				echo "		"$(eval_gettext "Enable or disable CT(Certificate Transparency) options.")
				echo "	"$(eval_gettext "Option: --no-register|--noregister")
				echo "		"$(eval_gettext "Do not register SCT files to CT(Certificate Transparency) log servers.")
				echo "		"$(eval_gettext "This Options only use with --ct Options.")
				echo "	"$(eval_gettext "Option: [profile]")
				echo "		"$(eval_gettext "Target Profile name. If do not specify it, use the current profile.")
				exit 0
				;;
			httpd)
				echo $(eval_gettext "HTTPd: Change using web server to Apache HTTPd.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			nginx)
				echo $(eval_gettext "NGINX: Change using web server to Nginx.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			php-fpm)
				echo $(eval_gettext "PHP-FPM: Change using PHP FastCGI server to PHP-FPM(version 5).")
				echo "	" $(eval_gettext "No need arguments.")
				exit 0
				;;
			php7)
				echo $(eval_gettext "PHP7: Change using PHP FastCGI server to PHP7.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			hhvm)
				echo $(eval_gettext "HHVM: Change using PHP FastCGI server to HHVM.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				exit 0
				;;
			target)
				echo $(eval_gettext "Target: Show or Change Profile.")
				echo "	"$(eval_gettext "No Argument:")
				echo "		"$(eval_gettext "Show the current profile name.")
				echo "	"$(eval_gettext "Argument: profile_name")
				echo "		"$(eval_gettext "Change profile to profile_name.")
				exit 0
				;;
			status)
				echo $(eval_gettext "Status: Show KUSANAGI middleware status and current profile.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			warm-up)
				echo $(eval_gettext "Warm up: Accerate HHVM Speed.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			configure)
				echo $(eval_gettext "Configure: Generate Configure file")
			 	echo "	"$(eval_gettext "If you change this server spec, please do this command to performance optimization.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			update)
				echo $(eval_gettext "Update: Update KUSANAGI plugin or certificate.")
				echo "	"$(eval_gettext "Argument: plugin [-y]")
				echo "		"$(eval_gettext "Update plugins If plugin version is updated.")
				echo "	"$(eval_gettext "Option: [-y]")
				echo "		"$(eval_gettext "Assume yes; assume that the answer to any question which would be asked is yes.")
				echo "	"$(eval_gettext "Argument: cert [profile]")
				echo "		"$(eval_gettext "Update Let's Encrypt SSL Certification.")
				echo "	"$(eval_gettext "Option: [profile]")
				echo "		"$(eval_gettext "Target Profile name. If do not specify it, use the current profile.")
				exit 0
				;;
			fcache)
				echo $(eval_gettext "FCache: Control FCache feature.")
				echo "	"$(eval_gettext "Argument: on")
				echo "		"$(eval_gettext "Use FCache")
				echo "	"$(eval_gettext "Argument: off")
				echo "		"$(eval_gettext "Do not use FCache")
				echo "	"$(eval_gettext "Argument: clear")
				echo "		"$(eval_gettext "Clear FCache")
				exit 0
				;;
			bcache)
				echo $(eval_gettext "BCache: Control BCache feature.")
				echo "	"$(eval_gettext "Argument: on")
				echo "		"$(eval_gettext "Use BCache")
				echo "	"$(eval_gettext "Argument: off")
				echo "		"$(eval_gettext "Do not use BCache")
				echo "	"$(eval_gettext "Argument: clear")
				echo "		"$(eval_gettext "Clear BCache")
				exit 0
				;;
			monit)
				echo $(eval_gettext "Monit: Control Monit(monitoring service) feature")
				echo "	"$(eval_gettext "No Argument:")
				echo "		"$(eval_gettext "Show monit status")
				echo "	"$(eval_gettext "Argument: on")
				echo "		"$(eval_gettext "Enable monit")
				echo "	"$(eval_gettext "Argument: off")
				echo "		"$(eval_gettext "Disable monit")
				echo "	"$(eval_gettext "Argument: config")
				echo "		"$(eval_gettext "Regenerate monit config file.")
				echo "	"$(eval_gettext "Argument: reload")
				echo "		"$(eval_gettext "Reload monit service.")
				exit 0
				;;
			zabbix)
				echo $(eval_gettext "Zabbix: Enable/Disable Zabbix Agent.")
				echo "	"$(eval_gettext "Argument: on")
				echo "		"$(eval_gettext "Enable Zabbix Agent.")
				echo "	"$(eval_gettext "Argument: off")
				echo "		"$(eval_gettext "Disable Zabbix Agent.")
				exit 0
				;;
			https)
				echo $(eval_gettext "HTTPS: Redirect/No-Redirect HTTP to HTTPS site to target profile.")
				echo "	"$(eval_gettext "Argument: redirect")
				echo "		"$(eval_gettext "Redirect HTTP to HTTPS site to target profile.")
				echo "	"$(eval_gettext "Argument: noredirect")
				echo "		"$(eval_gettext "Do not redirect HTTP to HTTPS site to target profile.")
				echo "	"$(eval_gettext "This option is obsolete.")
				exit 0
				;;
			autorenewal)
				echo $(eval_gettext "AutoRenewal: Enable/Disable Auto Renewal(Let's Encrypt certificate) feature.")
				echo "	"$(eval_gettext "Argument: on")
				echo "		"$(eval_gettext "Enable auto renewal Let's Encrypt certification.")
				echo "	"$(eval_gettext "Argument: off")
				echo "		"$(eval_gettext "Disable auto renewal Let's Encrypt certification.")
				echo "	"$(eval_gettext "This option is obsolete.")
				exit 0
				;;
			restart)
				echo $(eval_gettext "Restart: restart all enabled middleweres.")
				echo "	"$(eval_gettext "No need arguments.")
				exit 0
				;;
			remove)
				echo $(eval_gettext "Remove: remove setteing, contents, and DB.")
				echo "	"$(eval_gettext "Argument: [-y] [profile]")
				echo "	"$(eval_gettext "Option: -y")
				echo "		"$(eval_gettext "Assume yes; assume that the answer to any question which would be asked is yes.")
				echo "	"$(eval_gettext "Option: profile ")
				echo "		"$(eval_gettext "Target profile. When don't you set profile, you remove current profile.")
				exit 0
				;;
			images)
				echo $(eval_gettext "Optimize Image: Optimize JPEG/PNG files on target directories.")
				echo "	"$(eval_gettext "Argument: [options] [profile]")
				echo "	"$(eval_gettext "Option: --dir|--directory dirname")
				echo "		"$(eval_gettext "Set target directory. If you needs directories, You set like dir1:dir2:dir3.")
				echo "	"$(eval_gettext "Option: --jpg|--jpeg")
				echo "		"$(eval_gettext "Optimize JPEG files only.")
				echo "	"$(eval_gettext "Option: --png")
				echo "		"$(eval_gettext "Optimize PNG files only.")
				echo "	"$(eval_gettext "Option: --verbose")
				echo "		"$(eval_gettext "Put Verbose messages.")
				echo "	"$(eval_gettext "Option: --quality [1-100]")
				echo "		"$(eval_gettext "Set JPEG/PNG quality to 1-100 value. default value is 80.")
				echo "	"$(eval_gettext "Option: --resize [WIDTHxHEIGHT]")
				echo "		"$(eval_gettext "Resize images to specifed size. default value is 1280x1024.")
				echo "	"$(eval_gettext "Option: --color [1-256]")
				echo "		"$(eval_gettext "Reduce color to specified number(1-256). default value is 256.")
				echo "		"$(eval_gettext "This option is effective only png files.")
				echo "	"$(eval_gettext "Option: --strip")
				echo "		"$(eval_gettext "Remove comments data(like EXIF).This option is effective only JPEG files.")
				echo "	"$(eval_gettext "Option: --owner user[:group]")
				echo "		"$(eval_gettext "Modify owner:group to specified user and group. default value is kusanagi:kusanagi.")
				echo "	"$(eval_gettext "Option: --mode octed_value")
				echo "		"$(eval_gettext "Modify permissions to specified octed_value. default value is 0644.")
				echo "	"$(eval_gettext "Option: profile")
				echo "		"$(eval_gettext "Target profile. When don't you set profile, you remove current profile.")
				exit 0
				;;
			-h|--help|help)
				echo $(eval_gettext "Help: Help is this option.")
				exit 0
				;;
			*)
				echo $(eval_gettext "Invalid Parameters. Try 'kusanagi -h'")
				exit 1
				;;
		esac
		;;
	*)
		;;
	esac
}
