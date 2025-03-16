import dns.resolver
import sys
import concurrent.futures

def gather_cname_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        cname_records = [answer.to_text().rstrip('.') for answer in answers]
        return cname_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return []

def main(output_file=None, num_threads=1):
    # Read domains from standard input
    domains = sys.stdin.readlines()

    unique_cname_records = set()
    cname_queries = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_domain = {executor.submit(gather_cname_records, domain.strip()): domain for domain in domains}

        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            print(domain.rstrip())
            try:
                cname_records = future.result()
                for record in cname_records:
                    unique_cname_records.add(record.rstrip("."))
                cname_queries[domain] = cname_records
            except Exception as exc:
                print(f"Domain {domain} generated an exception: {exc}")

    if output_file:
        with open(output_file, 'w') as file:
            for record in unique_cname_records:
                file.write(record + '\n')
    else:
        for record in unique_cname_records:
            print(record)

    # Write CNAME query results to cname_queries.txt
    with open('cname_queries.txt', 'w') as file:
        for domain, records in cname_queries.items():
            file.write(f"Domain: {domain}\n")
            for record in records:
                file.write(f"  CNAME: {record}\n")
            file.write("\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gather CNAME records from a list of domains.")
    parser.add_argument('-t', type=int, default=1, help="Number of concurrent threads to run the CNAME queries")
    parser.add_argument('output_file', nargs='?', help="Optional output file to write the results")

    args = parser.parse_args()

    main(output_file=args.output_file, num_threads=args.t)
