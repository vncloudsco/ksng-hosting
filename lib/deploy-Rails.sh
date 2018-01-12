cd /home/kusanagi

/usr/local/bin/gem install rails
/bin/rails new $PROFILE -d ${RAILS_DB}

RAILS_BASE_DIR=/home/kusanagi/$PROFILE

chown -R kusanagi.kusanagi $RAILS_BASE_DIR

servers=(nginx httpd)
for server in ${servers[@]}; do
	echo 
	if [ ! -d ${RAILS_BASE_DIR}/log/${server} ]; then
		mkdir -p ${RAILS_BASE_DIR}/log/${server}
	fi
done

writable_dirs=(log tmp)
for dir in ${writable_dirs[@]}; do
	chown -R kusanagi.www ${RAILS_BASE_DIR}/${dir}
	chmod -R g+w ${RAILS_BASE_DIR}/${dir}
done

