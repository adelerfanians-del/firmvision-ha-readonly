# Fermvision Home Assistant integration

This repository contains a read-only local-polling Home Assistant integration
for Fermvision intercoms. It exposes reachability, device information, and
configured channel sensors. It does not contain gate-opening services or
unlock-command code.

Install through HACS as a custom repository with category **Integration**, or
copy `custom_components/fermvision` into Home Assistant's `config/custom_components` directory.

The integration sends only the read-only `get.device.qrcode` and
`get.device.attachInfo` requests. Device compatibility is not guaranteed.
