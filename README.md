# pyprologix
Classes to communicate to various devices using Prologix compatibe USB-GPIB-adapters

**Beware**: This is just a set of scripts to simplity communicating between a PC using a Prologix compatible USB-GPIB-adapter and some multimeters or other devices. Do **not** expect a full-fledged library or stable API between devices (yet?)

## Requirements

* pyserial

## Adapters

All adapters using a prologix compatible protocol should work. Adapters using different protocols like classic GPIB dongles are not supported. Most code was tested using fenrirs [GPIB-USBCDC](https://github.com/fenrir-naru/gpib-usbcdc) dongle.

## Devices

The main class can be used to communicate with most GPIB compatible devices. There are additional classes for specific devices imprementing the corresponding protocols.

### HP3478A

Most functions are supported. Additionally you can read calibration SRAM data to a file.

#### TODO/Whishlist

* Write calibration data

### Philips PM2534

Not yet implemented, WIP

### IEEE488.2/SCPI standard

Not yet implemented

## Clients

Consider these examples, not much functionality

### GUI

A simple TK gui showing current measurement value, function and range of a HP3478A multimeter. Requires pygubu.

### InfluxDB

A script polling a HP3478A multimeter every second and write the data to InfluxDB to be visualized using Grafana or Chronograf.
