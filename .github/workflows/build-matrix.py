#! /usr/bin/env python

import json
import os
import slugify

def main():
    containers_path = os.path.join('./containers')

    containers_list = list()
    for arch in sorted(os.listdir(containers_path)):
        arch_path = os.path.join(containers_path, arch)

        for vendor in sorted(os.listdir(arch_path)):
            vendor_path = os.path.join(arch_path, vendor)

            for board in sorted(os.listdir(vendor_path)):
                board_path = os.path.join(vendor_path, board)

                for file in sorted(os.listdir(board_path)):
                    if not (file == "Containerfile" or file == "Containerfile.in"):
                        continue

                    image_name = "bachi-{}-{}-{}".format(arch, slugify.slugify(vendor), slugify.slugify(board))
                    data = {
                        "name": "{} {}".format(vendor, board),
                        "image_name": image_name,
                        "path": os.path.join(board_path, file),
                        "dir": board_path,
                    }

                    test_file = os.path.join('./tests', arch, vendor, board, 'start-qemu.sh')
                    if os.path.exists(test_file):
                        data['qemu'] = test_file

                    containers_list.append(data)

    print(json.dumps({'containers': containers_list }))


if __name__ == '__main__':
    main()
