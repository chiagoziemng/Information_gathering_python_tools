import requests

# the domain to scan for subdomains

domain = "google.com"

# read all subdomains
with open("subdomains.txt") as file:
    # read all content
    content = file.read()
    #split by new lines

    subdomains = content.splitlines()

# a list of discovered subdomains
discovered_subdomains = []
for subdomain in subdomains:
    # construct the url
    url = f"http://{subdomain}.{domain}"

    try:
        # if this raises an Error, that means the subdomain does not exist
        requests.get(url)
    except requests.ConnectionError:
        # if the subdomian does not exist, just pass, print nothing
        pass
    else:
        print("[+] Discovered subdomain:" , url)

        # append the discovered subdomain to our list

        discovered_subdomains.append(url)

# save the discovered subdomians into a file
with open("discovered_subdomains.txt", "w") as f:

    for subdomain in discovered_subdomains:
        print(subdomain, file=f)