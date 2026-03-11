import re
from bs4 import BeautifulSoup


def extract_jd(subject, html_body):
    """
    Extract project title and description from a BTG/Catalant monitor alert email.
    Returns (title, description, platform).
    """
    # Title: strip "🔔 BTG: " or "🔔 Catalant: " prefix
    title = re.sub(r"^[^\w]*(?:BTG|Catalant)\s*:\s*", "", subject, flags=re.IGNORECASE).strip()
    platform = "BTG" if "btg" in subject.lower() else "Catalant"

    description = ""
    try:
        soup = BeautifulSoup(html_body, "html.parser")

        # Both BTG and Catalant emails put description in a <td colspan="2"> immediately
        # after the section header <td colspan="2"> that contains "Description".
        cells = soup.find_all("td", attrs={"colspan": "2"})
        for i, cell in enumerate(cells):
            if "Description" in cell.get_text() and i + 1 < len(cells):
                description = cells[i + 1].get_text(separator="\n", strip=True)
                break

        # Fallback: find the largest text block in the email
        if not description:
            all_tds = soup.find_all("td")
            if all_tds:
                longest = max(all_tds, key=lambda t: len(t.get_text(strip=True)))
                description = longest.get_text(separator="\n", strip=True)

    except Exception as e:
        print(f"  ⚠️  JD extraction error: {e}")

    return title, description, platform
