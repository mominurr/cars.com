# import necessary libraries
import  os,time,sys
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd

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


# scraping data from cars.com. this is the scraping main function
def data_collect(url):
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

    SCRAPED_DATA=[]

    page=1
    while page<=total_pages:

        # scraping progress show
        update_message(f"Scraping Progress: {page} out of total pages {total_pages}")

        scrape_url=f"{input_url}&page_size=100&page={page}"
        try:
            driver.get(scrape_url)
            time.sleep(1.5)
        except:
            pass

        try:
            soup=bs(driver.page_source,"html.parser")
        except:
            pass
        try:
            spark_button_tags=soup.find_all("spark-button",attrs={"class":"contact-by-phone"})
        except:
            spark_button_tags=[]
        if spark_button_tags is None:
            page+=1
            continue
        if len(spark_button_tags)==0:
            page+=1
            continue

        for tag in spark_button_tags:
            try:
                make=tag["data-make"]
            except:
                make=None
            try:
                model=tag["data-model"]
            except:
                model=None
            try:
                year=tag["data-year"]
            except:
                year=None
            try:
                trim=tag["data-trim"]
            except:
                trim=None
            try:
                price=tag["data-price"]
            except:
                price=None
            try:
                phone=tag["href"].split("tel:")[-1].strip()
                phone=str(phone)
            except:
                phone=None
            try:
                phone=phone.replace("+1-","").strip()
            except:
                pass
            try:
                data_listing_id=tag["data-listing-id"]
            except:
                data_listing_id=None
            try:
                div_tag=tag.find_parent("div").find_parent("div").find("div",attrs={"class":"vehicle-details"})
            except:
                pass
            try:
                stock_type=div_tag.find("p",attrs={"class":"stock-type"}).text.strip()
            except:
                stock_type=None
            try:
                title=div_tag.find("h2",attrs={"class":"title"}).text.strip()
            except:
                title=None
            try:
                price=div_tag.find("span",attrs={"data-qa":"primary-price"}).text.strip()
            except:
                price=None
            try:
                seller_name=div_tag.find("div",attrs={"class":"dealer-name"}).text.strip()
            except:
                seller_name=None

            data={
                "Id":data_listing_id,
                "Product URL":f"https://www.cars.com/vehicledetail/{data_listing_id}",
                "Title":title,
                "Make":make,
                "Model":model,
                "Year":year,
                "Trim":trim,
                "Price":price,
                "Stock Type":stock_type,
                "Price":price,
                "Seller Name":seller_name,
                "Phone Number":phone,
            }

            SCRAPED_DATA.append(data)

        page+=1

    print(f"\nTotal scraped data: {len(SCRAPED_DATA)}")
    date_str=time.strftime("%Y_%m_%d")
    filename=f"cars_data_{date_str}.csv"
    df=pd.DataFrame(SCRAPED_DATA)
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
    data_collect(url)

    print("\nScraping is Successfully Completed!\n")

    print("######################## THANKS FOR USING CARS.COM:SCRAPER ########################\n")




