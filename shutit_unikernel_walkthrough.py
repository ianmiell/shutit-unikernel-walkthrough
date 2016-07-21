import random
import string

from shutit_module import ShutItModule

class shutit_unikernel_walkthrough(ShutItModule):


	def build(self, shutit):
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		module_name = 'shutit_unikernel_walkthrough_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.send('rm -rf /tmp/' + module_name + ' && mkdir -p /tmp/' + module_name + ' && cd /tmp/' + module_name)
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file('/tmp/' + module_name + '/Vagrantfile','''
Vagrant.configure(2) do |config|
  config.vm.box = "''' + vagrant_image + '''"
  # config.vm.box_check_update = false
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.33.10"
  # config.vm.network "public_network"
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
    vb.name = "shutit_unikernel_walkthrough"
  end
end''')
		shutit.send('vagrant up --provider virtualbox',timeout=99999,check_exit=False)
		shutit.login(command='vagrant ssh')
		o = shutit.send_and_get_output('whoami')
		if o != 'ubuntu':
			shutit.pause_point('vagrant failed')
		shutit.login(command='sudo su -',password='vagrant')
		# cf. https://help.ubuntu.com/community/Xen
		shutit.install('xen-hypervisor-amd64',note='Install xen hypervisor')
		shutit.logout()
		shutit.logout()
		shutit.send('vagrant halt')
		shutit.send('vagrant up')
		shutit.login(command='vagrant ssh')
		o = shutit.send_and_get_output('whoami')
		if o != 'ubuntu':
			shutit.pause_point('vagrant failed')
		shutit.login(command='sudo su -',password='vagrant')
		shutit.send('vagrant up --provider virtualbox',timeout=99999,check_exit=False)
		shutit.install('opam',note='Install opam')
		shutit.multisend('opam init',{'Do you want OPAM to modify':'y'},note='Initialise opam')
		shutit.send('opam --version',note='Version should be at least 1.2.2')
		shutit.send('opam remote',note='Remotes should include opam.ocaml')
		o = shutit.send_and_get_output('ocaml -version',note='Should be 4.02.3+')
		if o != 'The OCaml toplevel, version 4.02.3':
			shutit.send('opam switch 4.02.3',note='Switch to 4.02.3+')
		shutit.send('eval `opam config env`',note='Set up en')
		shutit.install('m4')
		shutit.install('pkg-config')
		shutit.multisend('opam install mirage',{'Do you want to continue?':'Y'},note='Install mirage')
		shutit.install('git')
		if not shutit.file_exists('mirage-skeleton',directory=True):
			shutit.send('git clone git://github.com/mirage/mirage-skeleton.git && cd mirage-skeleton')
		else:
			shutit.send('cd mirage-skeleton && git pull')
		# UNIX
		shutit.send('cd console')
		shutit.send('mirage configure --unix',note='build for Unix binary target')
		shutit.send('make')
		shutit.send_until('./mir-console','world')
		# XEN
		shutit.install('libxen-dev')
		shutit.install('uuid-dev')
		shutit.install('xen-utils-common')
		shutit.send('mirage configure --xen',note='build for Xen target')
		shutit.send('make')
		shutit.send('xl create -c console.xml')
		shutit.pause_point('')

		shutit.logout()
		shutit.logout()
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/xenial64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')

		return True

	def test(self, shutit):

		return True

	def finalize(self, shutit):

		return True

	def isinstalled(self, shutit):

		return False

	def start(self, shutit):

		return True

	def stop(self, shutit):

		return True

def module():
	return shutit_unikernel_walkthrough(
		'vim8.shutit_unikernel_walkthrough.shutit_unikernel_walkthrough', 1264857475.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualbox.virtualbox.virtualbox','tk.shutit.vagrant.vagrant.vagrant']
	)

