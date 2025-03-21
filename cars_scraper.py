# import necessary libraries
import  os,time,sys
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
os.makedirs("data",exist_ok=True)

# display progress message
def update_message(message):
    """ Displays a progress message in the terminal, updating on the same line.

    Args:
        message (str): The message to display.
    """
    print(message,end='\r')
    sys.stdout.flush()



# ensuring the url is correctly structured for pagination scraping
def get_valid_inputurl(url):
    """Ensuring the url is correctly structured for pagination scraping.

    Args:
        url (str): The url is to be scraped.

    Returns:
        input_url (str): formatted url for pagination scraping.
    """
    input_url=None
    if url.find("&page_size=") != -1:
        if url.find("&page=") != -1:
            first_part=url[:url.find("&page=")]
            second_part=url[url.find("&page_size=")+1:]
            second_part=second_part[second_part.find("&"):]
            if second_part=="0":
                input_url=first_part
            else:
                input_url=first_part+second_part
        else:
            first_part=url[:url.find("&page_size=")]
            second_part=url[url.find("&page_size=")+1:]
            second_part=second_part[second_part.find("&"):]
            if second_part=="0":
                input_url=first_part
            else:
                input_url=first_part+second_part
    else:
        if url.find("&page=") != -1:
            first_part=url[:url.find("&page=")]
            second_part=url[url.find("&page=")+1:]
            second_part=second_part[second_part.find("&"):]
            if second_part=="0":
                input_url=first_part
            else:
                input_url=first_part+second_part
        else:
            input_url=url
    return input_url



# extracting total number of pages
def get_total_pages(input_url,driver):
    """Loads the webpage and extracts the total number of pages from the pagination links. This is important for navigating through multiple pages of search results.

    Args:
        input_url (str): The url is to be scraped.
        driver (webdriver): The webdriver is used to load the webpage.

    Returns:
        total_pages (int): The total number of pages.
    """
    try:
        driver.get(f"{input_url}&page_size=100")
        time.sleep(3)
    except:
        pass
    total_pages=1
    try:
        total_pages_str=bs(driver.page_source,"html.parser").find_all("a",attrs={"phx-click":"page_clicked"})[-1].text.strip()
        total_pages=int(total_pages_str)
    except:
        pass
    return total_pages


def get_text(soup, selector=None, tag=None, attr=None):
    """Extracts text or attribute value from a tag safely."""
    try:
        if tag:
            return tag.get(attr, None) if attr else tag.text.strip() if tag.text else None
        element = soup.select_one(selector) if selector else None
        return element.get(attr, None) if attr else element.text.strip() if element else None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def scrape_page(url, driver):
    """Loads a page and returns parsed HTML."""
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "contact-by-phone")))
    except:
        pass
    return bs(driver.page_source, "html.parser")

def extract_data(tag):
    """Extracts structured data from a listing."""
    try:
        div_tag = tag.find_parent("div").find_parent("div")
        price = tag.get("data-price", None)
        if price is None:
            price = get_text(div_tag, "span.primary-price")
        return {
            "Id": tag.get("data-listing-id", None),
            "Product URL": f"https://www.cars.com/vehicledetail/{tag.get('data-listing-id', '')}",
            "Title": get_text(div_tag, "h2.title"),
            "Make": tag.get("data-make", None),
            "Model": tag.get("data-model", None),
            "Year": tag.get("data-year", None),
            "Trim": tag.get("data-trim", None),
            "Price": price,
            "Stock Type": get_text(div_tag, "p.stock-type"),
            "Seller Name": get_text(div_tag, "div.dealer-name"),
            "Phone Number": tag.get("href", "").split("tel:")[-1].strip().replace("+1-", "") or None
        }
    except:
        return None

def get_data(url):
    """Scrapes data from the cars.com website. The data is then stored in a pandas dataframe. The dataframe is then written to a csv file. 

    Args:
        url (str): The url is to be scraped.

    Returns:
        None
    
    """
    input_url=get_valid_inputurl(url)
    if input_url is None:
        print("Please enter valid url!")
        os._exit(0)
    
    driver = webdriver.Chrome()

    total_pages=get_total_pages(input_url,driver)
    page = 1
    scraped_data = []

    while page <= total_pages:
        update_message(f"Progress: {page} out of pages {total_pages}")
        try:
            soup = scrape_page(f"{input_url}&page_size=100&page={page}", driver)

            for tag in soup.find_all("spark-button", class_="contact-by-phone"):
                data = extract_data(tag)
                if data:
                    scraped_data.append(data)
        except:
            pass

        page += 1


    print(f"\nTotal scraped data: {len(scraped_data)}")
    date_str=time.strftime("%Y_%m_%d")
    filename=os.path.join("data",f"cars_data_{date_str}.csv")
    df=pd.DataFrame(scraped_data)
    df.drop_duplicates(inplace=True,ignore_index=True,subset=["Id"])
    print("After removing duplicates, total data: ",len(df))
    df.to_csv(filename,index=False)
    print(f"Data saved as: {filename}")
    driver.quit()




if __name__ == '__main__':
    print("################### CARS.COM:SCRAPER ##################\n")
    url=input("Enter url: ")
    if len(url)==0:
        print("Please enter valid url!")
        os._exit(0)
    get_data(url)

    print("\nScraping is Successfully Completed!\n")

    print("######################## THANKS FOR USING CARS.COM:SCRAPER ########################\n")




