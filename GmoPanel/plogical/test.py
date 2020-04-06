import system_os
import os

os.chdir('/home/{}/{}/Up/'.format('kusanagi', 'themeonao.info'))
os.system('tar -xzf /home/{}/{}/Up/*.tar.gz'.format('kusanagi', 'themeonao.info'))
os.system('unzip -qq /home/{}/{}/Up/*.zip'.format('kusanagi', 'themeonao.info'))
os.system('gunzip -d /home/{}/{}/Up/*.sql.gz'.format('kusanagi', 'themeonao.info'))

list_file = system_os.find_file('/home/kusanagi/themeonao.info/Up/','index.php')
print(list_file)
