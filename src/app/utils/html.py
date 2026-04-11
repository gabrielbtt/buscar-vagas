from bs4 import BeautifulSoup
from app.schemas.job import NormalizedJob


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def parse_job_elements(
    html: str,
    source_name: str,
    item_selector: str,
    title_selector: str,
    location_selector: str,
    company_selector: str = None,
    url_selector: str = None
) -> list[NormalizedJob]:
    soup = parse_html(html)
    jobs = []
    
    items = soup.select(item_selector)
    
    for item in items:
        try:
            # Title
            title_el = item.select_one(title_selector)
            title = title_el.get_text(strip=True) if title_el else "Vaga sem título"
            
            # Location
            loc_el = item.select_one(location_selector)
            location = loc_el.get_text(strip=True) if loc_el else "Local não informado"
            
            # Company
            company = "Empresa não informada"
            if company_selector:
                comp_el = item.select_one(company_selector)
                if comp_el:
                    company = comp_el.get_text(strip=True)
            
            # URL
            url_str = ""
            if url_selector:
                url_el = item.select_one(url_selector)
                if url_el and url_el.has_attr('href'):
                    url_str = url_el['href']
            
            # Fallback for URL if not found and the item itself is an <a> tag
            if not url_str and item.name == 'a' and item.has_attr('href'):
                url_str = item['href']
            elif not url_str:
                # Try finding any link inside the item
                link_el = item.find('a', href=True)
                if link_el:
                    url_str = link_el['href']
            
            if not url_str:
                continue

            # Ensure URL is absolute (simple check)
            if url_str.startswith('/'):
                if "gupy" in source_name.lower():
                    url_str = f"https://portal.gupy.io{url_str}"
                elif "vagas" in source_name.lower():
                    url_str = f"https://www.vagas.com.br{url_str}"
            elif not url_str.startswith('http'):
                 if "gupy" in source_name.lower():
                    url_str = f"https://portal.gupy.io/{url_str.lstrip('/')}"
                 elif "vagas" in source_name.lower():
                    url_str = f"https://www.vagas.com.br/{url_str.lstrip('/')}"

            jobs.append(NormalizedJob(
                source_name=source_name,
                title=title,
                company=company,
                location=location,
                url=url_str, 
                work_model="Não informado",
                employment_type="Não informado",
                description_text=f"Vaga coletada da fonte {source_name}"
            ))
        except Exception as e:
            print(f"Erro ao parsear item em {source_name}: {e}")
            continue
            
    return jobs
