#!/bin/sh

SCRIPT_DIR="$(dirname "$0")"

exec \
	qemu-system-aarch64 \
		-M virt,secure=on,acpi=off \
		-bios "$SCRIPT_DIR/flash.bin" \
		-cpu cortex-a53 \
		-smp 2  \
		-m 2048 \
		-device virtio-blk-device,drive=hd0 \
		-device virtio-net-device,netdev=eth0 \
		-device virtio-rng-device,rng=rng0 \
		-netdev user,id=eth0 \
		-nographic \
		-object rng-random,filename=/dev/urandom,id=rng0 \
		-rtc base=utc,clock=host \
		-drive file="$1",if=none,format=raw,id=hd0
