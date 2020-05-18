# Raspberry Pi bike power LEDs

## Summary

This script reads power from your bike power meter and lights LEDs in a colour associated with your exertion.
It uses [pygatt](https://pypi.org/project/pygatt/) to talk to a Bluetooth powermeter and a NeoPixel ring to display the colours.

## Setup

In the `config.yml` file you will need to configure the power meter details and your FTP.

[This guide](https://www.jaredwolff.com/get-started-with-bluetooth-low-energy/#!) is a good start to using finding this information on a Raspberry Pi:

- `hcitool dev` - this will check whether `hcitool` can see your bluetooth adapter
- `sudo hcitool lescan` - this performs a BLE scan and lists the addresses of the visible devices

### config.yml

The following is a sample `config.yml` file:

    bluetooth-device: c1:70:6d:98:63:29
    ftp: 245
    power-average-duration: 3


### Cycling Power Measurement characteristic

This script reads the [Cycling Power Measurement](https://www.bluetooth.com/xml-viewer/?src=https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.cycling_power_measurement.xml).
This contains the vast majority of the power data but the only part we are interested in is the `Instantaneous Power` part which is held in the second 16 bits (bits 17-32, inclusive).

When learning about Bluetooth data [this tool](https://cryptii.com/pipes/integer-encoder) was invaluable for exploring the raw data.

pygatt requires a long UUID for the characteristic but the Bluetooth spec provides only a short UUID.
[This GitHub comment](https://github.com/peplin/pygatt/issues/140#issuecomment-330105261) describes how to convert from the short UUID to the long UUID.
   
## Zwift colours

This script uses the same colours as Zwift.
Thanks to [this GPLama video](https://www.youtube.com/watch?v=bOZtysy-L2w) for the Zwift colours:

- Grey: <= 59%
- Blue: 60%-75%
- Green: 76%-89%
- Yellow: 90%-104%
- Orange: 105%-118%
- Red: >= 119%

## pipenv and setup

This project uses [pipenv](https://pypi.org/project/pipenv/) to manage dependencies and virtual environments.
I found that installing dependencies would result in a timeout on the Pi, [this article](https://stackoverflow.com/a/58329272) pointed me in the direction of setting `export PIPENV_TIMEOUT=9999` and it seems to work well.

Running `setup.sh` on a Raspberry Pi should set everything up.
This was developed using a Raspberry Pi 3 running _Raspbian Buster_ (the latest version at the time of writing).

To control the LEDs the script must be run with `sudo`, doing so [means virtual environment variables etc can't be accessed](https://askubuntu.com/a/245921) in the same way.
You must explicitly specify the location of your virtual environment.
Run `pipenv --venv` to find the location of your virtual environment, something like this:

    /home/pi/.local/share/virtualenvs/power-led-EXGU0oXn

You can then run the following:

    sudo /home/pi/.local/share/virtualenvs/power-led-EXGU0oXn/bin/python3 power.py
    
Alternatively you can add the following shebang to the top of the script

    #!/home/pi/.local/share/virtualenvs/power-led-EXGU0oXn/bin/python3
    
and then run the script using using:

    sudo ./power.py 

## Running the script on startup

To run the script at startup add the following line to `/etc/rc.local`:

    sudo /home/pi/Documents/power-led/power.py &
    
This assumes you have added the shebang as described in the section above.
Adjust the directories accordingly.
