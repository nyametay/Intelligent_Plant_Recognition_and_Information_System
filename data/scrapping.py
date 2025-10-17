from bs4 import BeautifulSoup
import requests
import urllib.parse
import base64


# This transforms the numbers to a message
def watering_message(watering):
    watering_data = None
    if watering is not None:
        if watering['max'] is not None and watering['min'] is not None:
            max_water = int(watering['max'])
            min_water = int(watering['min'])
            if min_water == 1 and max_water == 2:
                watering_data = 'Needs no or moderate watering, keep the soil moist or dry.'
            elif min_water == 1 and max_water == 3:
                watering_data = 'Needs moderate watering, keep the soil moist but not waterlogged.'
            elif min_water == 2 and max_water == 3:
                watering_data = 'Needs moderate or more watering, keep the soil moist or waterlogged.'
            elif min_water == 1 and max_water == 1:
                watering_data = 'Needs no watering, keep the soil dry.'
            elif min_water == 2 and max_water == 2:
                watering_data = 'Needs moderate watering, keep soil moist.'
            elif min_water == 3 and max_water == 3:
                watering_data = 'Needs more watering, keep soil waterlogged.'
    else:
        watering_data = "None"
    return watering_data


# This truncates the words so that all have the same word limits
def truncate_words(sentence, word_limit):
    if sentence is not None:
        words = sentence.split()
        if len(words) <= word_limit:
            return sentence
        truncated = ' '.join(words[:word_limit])
        return truncated + "..."
    return None


# This generates the severity level of the disease
def generate_category(number):
    number = int(number)
    if 0 <= number <= 0.25:
        return 'Mild'
    elif 0.25 < number <= 0.5:
        return 'Moderate'
    elif 0.5 < number <= 0.75:
        return 'Serious'
    elif number > 0.75:
        return 'Critical'


# This searches for the page by the common name
def search_pfaf_by_name(name):
    search_url = f"https://pfaf.org/user/DatabaseSearhResult.aspx?CName=%{urllib.parse.quote(name)}%"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('table', id='ContentPlaceHolder1_gvresults')


# This finds the exact page url and the latin name of the plant
def find_plant_page_by_name(common_name, botanical_name):
    result_table = search_pfaf_by_name(common_name)
    botanical_name = botanical_name.split(' ')[0]
    if not result_table and len(common_name.split()) > 1:
        parts = common_name.split()
        result_table_a = search_pfaf_by_name(parts[0])
        result_table_b = search_pfaf_by_name(parts[1])
    else:
        result_table_b = result_table_a = result_table

    def check_table(result_table_):
        if not result_table_:
            return None, None
        rows = result_table_.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 2:
                continue
            latin_name_ = columns[0].get_text().strip()
            common_name_ = columns[1].get_text().strip()
            if botanical_name.lower() in latin_name_.lower() or common_name.lower() in common_name_.lower():
                return latin_name_, f"https://pfaf.org/user/Plant.aspx?LatinName={urllib.parse.quote(latin_name_)}"
        return None, None

    latin_name, plant_page_url = check_table(result_table_a)
    if not plant_page_url:
        latin_name, plant_page_url = check_table(result_table_b)

    return latin_name, plant_page_url


# This gets the medical uses from the pfaf page
def scrape_medical_uses(soup):
    # Find the section containing Medicinal Uses (case-insensitive, robust)
    medicinal_uses_section = soup.find(lambda tag: tag.name == 'h2' and 'medicinal' in tag.get_text(strip=True).lower())

    if not medicinal_uses_section:
        print("Medicinal Uses section not found on the page")
        return None

    # Find the parent div with class 'boots2' containing Medicinal Uses content
    boots2_div = medicinal_uses_section.find_next('div', class_='boots2')

    if not boots2_div:
        print("Unable to locate the 'boots2' class for Medicinal Uses")
        return None

    medicinal_uses = []
    next_element = boots2_div.find_next()

    while next_element:
        if next_element.name == 'small' and 'text-muted' in next_element.get('class', []):
            break

        for br_tag in next_element.find_all('br'):
            br_tag.replace_with('\n')
        for i_tag in next_element.find_all('i'):
            i_tag.decompose()

        if len(next_element.find_all('a')) == 0:
            medicinal_uses.append(next_element.get_text(strip=True))
        else:
            medicinal_uses.append(next_element.find_all(string=True)[-2])
        next_element = next_element.find_next_sibling()

    return medicinal_uses


# This gets the edible uses from the pfaf page
def scrape_edible_uses(soup):
    # Find the section containing Edible Uses (case-insensitive)
    edible_uses_section = soup.find(lambda tag: tag.name == 'h2' and 'edible' in tag.get_text(strip=True).lower())

    if not edible_uses_section:
        print("Edible Uses section not found on the page")
        return None

    boots3_div = edible_uses_section.find_next('div', class_='boots3')

    if not boots3_div:
        print("Unable to locate the 'boots3' class for Edible Uses")
        return None

    edible_parts = []
    edible_uses = []

    next_element = boots3_div.find_next()

    while next_element:
        if next_element.name == 'small' and 'text-muted' in next_element.get('class', []):
            break

        for br_tag in next_element.find_all('br'):
            br_tag.replace_with('\n')
        for i_tag in next_element.find_all('i'):
            i_tag.decompose()

        if "Edible Part" in next_element.get_text():
            edible_part_tags = next_element.find_all('a')
            for tag in edible_part_tags:
                edible_parts.append(tag.get_text(separator='\n', strip=True))

        if 'Edible Uses' in next_element.get_text():
            edible_uses.append(next_element.find_all(string=True)[-2])
        else:
            edible_uses.append(next_element.get_text(strip=True))
        next_element = next_element.find_next_sibling()

    return edible_parts, edible_uses


# This gets the other uses from the pfaf page
def scrape_other_uses(soup):
    # Find the section containing Other Uses (case-insensitive)
    other_uses_section = soup.find(lambda tag: tag.name == 'h2' and 'other uses' in tag.get_text(strip=True).lower())

    if not other_uses_section:
        print("Other Uses section not found on the page")
        return None

    boots4_div = other_uses_section.find_next('div', class_='boots4')

    if not boots4_div:
        print("Unable to locate the 'boots4' class for Other Uses")
        return None

    other_uses = []
    next_element = boots4_div.find_next()

    while next_element and next_element.name != 'h3':
        if len(next_element.find_all('a')) == 0:
            text = next_element.get_text().strip()
            if text:
                other_uses.append(text)
        else:
            strings = next_element.find_all(string=True)
            if 'Special Uses' in strings:
                special_index = strings.index('Special Uses')
                if special_index > 0:
                    other_uses.append(strings[special_index - 1].strip())
            else:
                if strings[-1].strip():
                    other_uses.append(strings[-1].strip())

        next_element = next_element.find_next_sibling()

    return other_uses


# This gets the plant uses by checking pfaf
def get_plant_uses_pfaf(common_name, botanical_name):
    latin_name, plant_page_url = find_plant_page_by_name(common_name, botanical_name)
    if not plant_page_url:
        return None
    response = requests.get(plant_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    medicinal_uses = scrape_medical_uses(soup)
    edible_parts, edible_uses = scrape_edible_uses(soup)
    other_uses = scrape_other_uses(soup)

    uses = {
        'Other Uses': other_uses,
        'Edible Parts': edible_parts,
        'Edible Uses': edible_uses,
        'Medicinal Uses': medicinal_uses
    }

    return uses


# This gets the plant uses by checking wikipedia
def get_plant_use_wikipedia(plant_name):
    plant_name = plant_name.replace(' ', '_')
    url = f"https://en.wikipedia.org/wiki/{plant_name}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    parent = None
    for header in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        if 'Uses' in header.text:
            parent = header.find_parent("div")
            break

    if parent is None:
        return None

    paragraphs = []
    next_sibling = parent.find_next_sibling()
    while next_sibling:
        if next_sibling.name == 'p':
            paragraphs.append(next_sibling.text.strip())
        elif 'mw-heading' in next_sibling.get('class', []):
            break
        next_sibling = next_sibling.find_next_sibling()

    if len(paragraphs) >= 1:
        return paragraphs
    else:
        return None


# This gets the uses from Google
def get_google_uses(common_name):
    def google_search(query_, api_key_, cse_id_, num=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {'q': query_, 'key': api_key_, 'cx': cse_id_, 'num': num}
        response = requests.get(url, params=params)
        return response.json()

    api_key = 'AIzaSyDybQAwDNM4X_yiIqDjtR9IZS83QhIQlfM'
    cse_id = '9321b59816bac4ca6'
    common_name = common_name.replace('-', ' ') if '-' in common_name else common_name
    query = f'{common_name} uses'

    results = google_search(query, api_key, cse_id)

    if 'items' in results:
        for item in results['items']:
            snippet = item.get('snippet')
            if snippet:
                link = item.get('link')
                if link:
                    return {'snippet': snippet, 'link': link}
                break
    else:
        print("No results found")
        link = 'https://www.google.com/search?q={urllib.parse.quote(common_name)}+uses'
        return {'None': link}


# This gets the plant uses by checking pfaf if no result is returned then checks wikipedia
def get_plant_uses(common_name, botanical_name):
    uses = get_plant_uses_pfaf(common_name, botanical_name)
    if uses:
        return uses
    else:
        wikipedia_info = get_plant_use_wikipedia(common_name)
        return wikipedia_info


# Gets the plant uses the family name and botanical name
def search_pfaf_by_family(family):
    search_url = f"https://pfaf.org/user/search_name.aspx?family={urllib.parse.quote(family)}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('table', id='ContentPlaceHolder1_gvresults')


def find_plant_page_by_family(family_name, botanical_name):
    result_table = search_pfaf_by_family(family_name)
    botanical_name_ = botanical_name.split(' ')[0]

    def check_table_family(result_table_):
        if not result_table_:
            return None, None
        rows = result_table_.find_all('tr')[1:]
        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 2:
                continue
            latin_name_ = columns[0].get_text().strip()
            common_name_ = columns[1].get_text().strip()
            family_name_ = columns[2].get_text().strip()
            if botanical_name_.lower() in latin_name_.lower() or family_name.lower() in family_name_.lower():
                return latin_name_, f"https://pfaf.org/user/Plant.aspx?LatinName={urllib.parse.quote(latin_name_)}", common_name_
        return None, None

    latin_name, plant_page_url, common_name = check_table_family(result_table)
    return latin_name, plant_page_url, common_name


def get_plant_uses_pfaf_family(family_name, botanical_name):
    latin_name, plant_page_url, common_name = find_plant_page_by_family(family_name, botanical_name)
    if not plant_page_url:
        return None
    response = requests.get(plant_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    medicinal_uses = scrape_medical_uses(soup)
    edible_parts, edible_uses = scrape_edible_uses(soup)
    other_uses = scrape_other_uses(soup)
    uses = {
        'Other Uses': other_uses,
        'Edible Parts': edible_parts,
        'Edible Uses': edible_uses,
        'Medicinal Uses': medicinal_uses
    }
    return uses, common_name


def get_plant_uses_family(family_name, botanical_name):
    uses, common_name = get_plant_uses_pfaf_family(family_name, botanical_name)
    botanical_name = botanical_name.replace('-', ' ') if '-' in botanical_name else botanical_name
    query = f"{botanical_name} uses"
    if uses:
        return uses, common_name
    else:
        wikipedia_info = get_plant_use_wikipedia(botanical_name)
        if wikipedia_info is None:
            google_search = get_google_uses(query)
            return google_search, common_name
        return wikipedia_info, common_name


# This gets the plant description from the wikipedia page
def get_plant_description_wikipedia(plant_name):
    plant_name = plant_name.split(' ')
    if 'x' in plant_name:
        plant_name.remove('x')
        plant_name = ' '.join(plant_name)
    else:
        plant_name = '_'.join(plant_name)
    plant_name = plant_name.replace(' ', '_')
    url = f"https://en.wikipedia.org/wiki/{plant_name}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    parent = soup.find('div', class_='mw-content-ltr mw-parser-output')
    if parent is None:
        return None

    paragraphs = []
    next_sibling = parent.find_next()
    while next_sibling:
        if next_sibling.name == 'p' and len(next_sibling.text.strip()) != 0:
            paragraphs.append(next_sibling.text.strip())
        elif 'mw-heading' in next_sibling.get('class', []):
            break
        next_sibling = next_sibling.find_next_sibling()

    if len(paragraphs) >= 1:
        return paragraphs
    else:
        return None


def search_images_and_encode_first(query):
    api_key = "AIzaSyDybQAwDNM4X_yiIqDjtR9IZS83QhIQlfM"
    search_engine_id = "9321b59816bac4ca6"
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}&searchType=image"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["items"]:
            first_image_url = data["items"][0]["link"]
            image_response = requests.get(first_image_url)
            image_response.raise_for_status()
            image_data = image_response.content
            base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
            return base64_encoded_data
        else:
            print("No images found for the query.")
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching images:", e)
        return None
