"""Compare two domain lists and print differences plus intersection."""

import argparse
import os
import re
from urllib.parse import urlparse


DOMAIN_CLEAN_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?P<domain>[A-Za-z0-9.-]+)")


def normalize_domain(line: str) -> str:
    line = line.strip()
    if not line or line.startswith("#"):
        return ""
    parsed = urlparse(line if line.startswith("http") else f"http://{line}")
    domain = parsed.netloc or parsed.path
    domain = domain.lower().strip("./ ")
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def read_domains(path: str) -> set[str]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    domains = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            domain = normalize_domain(raw)
            if domain:
                domains.add(domain)
    return domains


def write_list(path: str, items: set[str]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for item in sorted(items):
            fh.write(f"{item}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two domain lists and report unique domains and intersection."
    )
    parser.add_argument("file1", help="First domain list file")
    parser.add_argument("file2", help="Second domain list file")
    parser.add_argument(
        "--out-prefix",
        default=None,
        help="Optional prefix to write output files: uniq1.txt, uniq2.txt, common.txt",
    )
    args = parser.parse_args()

    domains1 = read_domains(args.file1)
    domains2 = read_domains(args.file2)

    only1 = domains1 - domains2
    only2 = domains2 - domains1
    common = domains1 & domains2

    print(f"{args.file1}: {len(domains1)} domains")
    print(f"{args.file2}: {len(domains2)} domains")
    print(f"Common domains: {len(common)}")
    print(f"Only in {args.file1}: {len(only1)}")
    print(f"Only in {args.file2}: {len(only2)}")
    print()

    if args.out_prefix:
        write_list(f"{args.out_prefix}_only_in_1.txt", only1)
        write_list(f"{args.out_prefix}_only_in_2.txt", only2)
        write_list(f"{args.out_prefix}_common.txt", common)
        print("Output files written:")
        print(f"  {args.out_prefix}_only_in_1.txt")
        print(f"  {args.out_prefix}_only_in_2.txt")
        print(f"  {args.out_prefix}_common.txt")


if __name__ == "__main__":
    main()
