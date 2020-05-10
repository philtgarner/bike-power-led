# Raspberry Pi bike power LEDs

## Summary

This script reads power from your bike power meter and lights LEDs in a colour associated with your exertion.
It uses [pygatt](https://pypi.org/project/pygatt/) to talk to a Bluetooth powermeter.

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
