import dns.resolver
import requests
from bs4 import BeautifulSoup
import sublist3r

def dns_query(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False

def find_subdomains(domain):
    subdomains = []
    common_subdomains = ['www', 'mail', 'ftp', 'test', 'dev', 'api', 'blog', 'shop']

    for subdomain in common_subdomains:
        full_domain = f"{subdomain}.{domain}"
        if dns_query(full_domain):
            subdomains.append(full_domain)
    
    return subdomains

def google_search(domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    query = f"site:{domain} -www"
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    subdomains = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and domain in href:
            start_idx = href.find('://') + 3
            end_idx = href.find('/', start_idx)
            subdomain = href[start_idx:end_idx]
            if subdomain.endswith(domain) and subdomain != domain:
                subdomains.add(subdomain)
    return list(subdomains)

def sublist3r_search(domain):
    subdomains = sublist3r.main(domain, 40, savefile=None, ports=None, silent=True, verbose=False, enable_bruteforce=False, engines=None)
    return subdomains

def enumerate_subdomains(domain):
    print(f"Enumerando subdominios de {domain}...")

    subdomains = set()

    # Agregar subdominios encontrados por consultas DNS comunes
    subdomains.update(find_subdomains(domain))

    # Agregar subdominios encontrados mediante búsqueda en Google
    google_subdomains = google_search(domain)
    subdomains.update(google_subdomains)

    # Agregar subdominios encontrados mediante Sublist3r
    sublist3r_subdomains = sublist3r_search(domain)
    subdomains.update(sublist3r_subdomains)

    return list(subdomains)

if __name__ == "__main__":
    domain = input("Ingrese el dominio: ")
    subdomains = enumerate_subdomains(domain)
    if subdomains:
        print(f"Subdominios encontrados para {domain}:")
        for sub in subdomains:
            print(sub)
    else:
        print(f"No se encontraron subdominios para {domain}.")

