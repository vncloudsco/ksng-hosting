# kusanagi update

# load functions
if [ 0 -ne $(type eval_gettext > /dev/null 2>&1 ; echo $?) ] ; then
	export TEXTDOMAIN=kusanagi
	source /usr/bin/gettext.sh
fi
if [ 0 -ne $(type k_generate_seckey > /dev/null 2>&1 ; echo $?) ] ; then
	source /usr/lib/kusanagi/lib/functions.sh
fi

echo $(eval_gettext "Updating..")

cat /etc/nginx/nginx.conf | grep 'server_names_hash_bucket_size ' > /dev/null
RET=$?
if [ $RET -eq 1 ] ; then
    sed -i 's/charset UTF-8;/charset UTF-8;\n   server_names_hash_bucket_size 128;/' /etc/nginx/nginx.conf
fi

cat /etc/hosts.allow | grep 'all : 127.0.0.1 \[::1\]' > /dev/null
RET=$?
if [ $RET -eq 1 ] ; then
    sed -i 's/all : 127.0.0.1/all : 127.0.0.1 [::1]/' /etc/hosts.allow
fi

if [ ! -e /usr/bin/php7 ]; then
    ln -s /usr/local/php7/bin/php /usr/bin/php7
fi
cat /etc/yum.conf | grep 'exclude=httpd* ' > /dev/null
RET=$?
if [ $RET -eq 1 ] ; then
    echo 'exclude=httpd*' >> /etc/yum.conf
fi
cat /etc/yum.conf | grep 'exclude=pecl-php-apcu ' > /dev/null
RET=$?
if [ $RET -eq 1 ] ; then
    echo 'exclude=php-pecl-apcu' >> /etc/yum.conf
fi

# Improve Security
# use this update after kusanagi init
getent shadow kusanagi | egrep '^kusanagi:!!:' 2>&1 > /dev/null
RET=$?
if [ $RET -ne 0 ] ; then
	# generate security keys when kusanagi provision already set
	k_generate_seckey shrink
	echo Done
fi

# rename mod_cimprov.conf when Azure
MOD_CIMPROV=" /etc/httpd/conf.d/mod_cimprov.conf"
RET=$(grep azure /etc/kusanagi 2>&1 > /dev/null; echo $?)
if [ $RET -eq 0 -a -f ${MOD_CIMPROV} ] ; then
	mv ${MOD_CIMPROV} ${MOD_CIMPROV}.orig
fi

# Let's Encrypt
if [ ! -e /usr/local/certbot/certbot-auto ] ; then
	cd /usr/local/
	git clone https://github.com/certbot/certbot.git
	/usr/local/certbot/certbot-auto --help
fi
if [ ! -e /usr/local/letsencrypt/letsencrypt-auto ]; then
    cd /usr/local/
    rm -rf letsencrypt-auto
fi
# permission check
find /home/*/DocumentRoot -type d -name uploads -prune -o -user root -exec chown kusanagi:kusanagi {} \; 2> /dev/null

if [ -e "/etc/cloud/cloud.cfg" ] ; then
	grep "preserve_hostname: "
	if [ "$?" -eq 1 ] ; then
		echo "preserve_hostname: true" >> /etc/cloud/cloud.cfg
	fi
fi

# check php lib's owner and permission
find /var/lib/php -maxdepth 1 -type d -exec chown root:www {} \; -exec chmod 770 {} \;

# monit enable
k_monit monit on

# remove nginx repository
# add zabbix 3.0
RET=$(rpm -q zabbix-release 2>&1 > /dev/null; echo $?)
if [ $RET -eq 1 ] ; then
	nohup sh -c '(rpm -ivh http://repo.zabbix.com/zabbix/3.0/rhel/7/x86_64/zabbix-release-3.0-1.el7.noarch.rpm;
	rpm -q zabbix22-agent 2>&1 > /dev/null && rpm -e --nodeps zabbix22 zabbix22-agent;
	rpm -q nginx-release-centos 2>&1 > /dev/null && rpm -e nginx-release-centos;
	yum clean all; sleep 10;
	yum install zabbix-agent -y )' > /dev/null &
fi

#bash_completion
cat /root/.bashrc | grep '/etc/bash_completion.d/kusanagi' > /dev/null
RET=$?
if [ $RET -eq 1 ] ; then
	source '/etc/bash_completion.d/kusanagi'
    echo "source '/etc/bash_completion.d/kusanagi'" >> /root/.bashrc
fi
