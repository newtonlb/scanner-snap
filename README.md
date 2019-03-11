# the scanner-snap !
A snap provided by [Beaconinside](https://www.beaconinside.com)  to detect proximity beacons and send its data to our context API .

## Installation 
 first, we need to build the snap
```
sudo snapcraft
```
after the build is over the snap binary is generated . to install it run 
```
sudo snap install scanner_0.1_amd64.snap --dangerous

```
## how to use 
first, enable bluetooth interface
```
sudo hciconfig hci0 up 
```
The next step is to connect the snap to the needed interfaces . some interfaces may be automatically connected depending on your hardware . You can check their status by :

```
snap interfaces scanner 
```
then connect the missing ones . Here is the commands (you won't use them all )
```
snap connect scanner:bluetooth-control :bluetooth-control
snap connect scanner:network :network 
snap connect scanner:network-observe :network-observe
snap connect scanner:network-bind :network-bind
snap connect scanner:serial-port :caracalla:ttys4

```
note that you need to identify the slot to connect the serial-port plug to , which corespounds to the port on which the GPS chipset is mounted. On our case it's ttys4.

finally to run the snap you can  
```
sudo  snap run scanner 
```
or 
```
sudo  scanner 
```
to use the GPS location 
```
sudo snap run scanner --gps-enabled --gateway-type static
```
for more options 
```
sudo scanner -h | --help
```
