genrss on OpenShift
===================

Running on OpenShift
----------------------------

Create an account at https://www.openshift.com/

Create a python application based on the code in this repository

    rhc app create genrss python-3.3

Add the cron scheduler cartridge to your new application:
	
	$ rhc cartridge add cron -a genrss

Enable all of your scripts:

	$ rhc cartridge start cron -a genrss

Add the codes, git add, git commit then git push.

That's it, you can now checkout your application at:

    http://boxy-$yournamespace.rhcloud.com