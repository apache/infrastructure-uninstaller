# infrastructure-uninstaller
ASF Infrastructure Application Uninstaller

Uninstalls older versions of known programs that are now pipservices:

- blocky
- kif
- loggy

Runs once (per install or per restart) and scans through the systemd lib 
and filesystem for whether these apps are installed, and removes them 
completely if found, by:

- stopping the service
- disabling the service
- removing all systemd/upstart files
- removing all application files
- removing the application main directory
- reloading systemd
- resetting any found failures in systemd

It may be installed on one or more nodes via pipservice, as such:

~~~yaml
pipservice:
   uninstaller:
     tag: master
~~~
