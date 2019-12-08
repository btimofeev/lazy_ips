#!/usr/bin/env python3

from lazy_ips.patch import ips
import argparse


def main():
    parser = argparse.ArgumentParser(description="Apply IPS patch to ROM image")
    parser.add_argument("image_file")
    parser.add_argument("patch_file")

    args = parser.parse_args()

    try:
        image = open(args.image_file, 'rb+')
    except Exception as err:
        print(f"Error opening {args.image_file}: {err}")
        exit()

        try:
            patch = open(args.patch_file, 'rb')
        except Exception as err:
            print(f"Error opening {args.patch_file}: {err}")
            exit()

        try:
            for patch_line in ips.read_patch(patch):
                ips.apply_patch_line(image, patch_line)
        except Exception as err:
            print(f"Error patching {args.image_file}: {err}")
        finally:
            patch.close()
            image.close()


if __name__ == "__main__":
    main()
