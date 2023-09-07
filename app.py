from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# Don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # Do not change this

# Insert the scraping here
url_get = requests.get('https://www.kalibrr.id/id-ID/job-board/te/data/')
soup = BeautifulSoup(url_get.content, "html.parser")

# Find your right key here
table = soup.find('div', attrs={'class':'k-border-b k-border-t k-border-tertiary-ghost-color md:k-border md:k-overflow-hidden md:k-rounded-lg'})
row = table.find_all('div', attrs={'class':'k-grid k-border-tertiary-ghost-color k-text-sm k-p-4 md:k-p-6 css-1b4vug6'})

row_length = len(row)

temp = []

# Base URL for the job listings
base_url = 'https://www.kalibrr.id/id-ID/job-board/te/data/'

# Loop through a range of page numbers
for page_number in range(1, 15):
    # Create the full URL for the current page
    page_url = base_url + str(page_number) + '/'
    
    # Send an HTTP GET request to the page
    response = requests.get(page_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the job listings table
        table = soup.find('div', attrs={'class': 'k-border-b k-border-t k-border-tertiary-ghost-color md:k-border md:k-overflow-hidden md:k-rounded-lg'})
        
        # Check if the table was found
        if table:
            # Find the length of the elements you want to scrape
            elements_length = len(table.find_all('div', attrs={'class': 'k-col-start-3 k-row-start-1'}))
            
            # Loop through the elements and scrape data
            for i in range(elements_length):
                title = table.find_all('div', attrs={'class': 'k-col-start-3 k-row-start-1'})[i].text
                
                lokasi = table.find_all('a', attrs={'class': 'k-text-subdued k-block'})[i].text.strip()
                
                data_pekerjaan = table.find_all('span', attrs={'class': 'k-block k-mb-1'})[i].text.split('•')
                tanggal_post = data_pekerjaan[0].strip()
                tanggal_deadline = data_pekerjaan[1].strip()
                
                perusahaan = table.find_all('span', attrs={'class': 'k-inline-flex k-items-center k-mb-1'})[i].text
                
                # Append the scraped data as a tuple to the temp list
                temp.append((title, lokasi, tanggal_post, tanggal_deadline, perusahaan))

temp = temp[::-1]

# Change into a DataFrame
df = pd.DataFrame(temp, columns = ('Title','Lokasi','Tanggal Post', 'Tanggal Deadline','Perusahaan'))

# Insert data wrangling here

#Tanggal (Penghilangan 'Posted - days ago')
df['Tanggal Post'] = df['Tanggal Post'].str.replace('Posted','')
#Tanggal (Penghilangan 'Apply before-')
df['Tanggal Deadline'] = df['Tanggal Deadline'].str.replace('Apply before','')
# Lokasi (astype menjadi category)
df['Lokasi'] = df['Lokasi'].astype('category')
# Lokasi (astype menjadi category)
df['Lokasi'] = df['Lokasi'].str.replace(', Indonesia','')

#Renaming Jakarta jobs
jakarta_mapping = {
    'East Jakarta': 'Jakarta',
    'Jakarta Selatan': 'Jakarta',
    'Central Jakarta City': 'Jakarta',
    'West Jakarta': 'Jakarta',
    'Kota Tangerang Selatan': 'Jakarta',
    'South Jakarta': 'Jakarta',
    'Central Jakarta': 'Jakarta',
    'Jakarta Pusat': 'Jakarta',
    'North Jakarta': 'Jakarta',
    'Kota Jakarta Barat': 'Jakarta',
    'Jakarta Timur': 'Jakarta',
    'Jakarta Utara': 'Jakarta',
    'Jakarta Barat': 'Jakarta',
    'Kota Jakarta Pusat': 'Jakarta',
    'Kota Jakarta Selatan': 'Jakarta'
}
df['Lokasi'] = df['Lokasi'].replace(jakarta_mapping)

#Renaming Tangerang jobs
tangerang_mapping = {
    'Tangerang Kota': 'Tangerang'
}
df['Lokasi'] = df['Lokasi'].replace(tangerang_mapping)

#Renaming Tangerang Selatan
tangerangselatan_mapping = {
    'South Tangerang': 'Tangerang Selatan'
}
df['Lokasi'] = df['Lokasi'].replace(tangerangselatan_mapping)

#Renaming Bandung
bandung_mapping = {
    'Bandung Kota': 'Bandung'
}
df['Lokasi'] = df['Lokasi'].replace(bandung_mapping)


# End of data wrangling

@app.route("/")
def index():

        #Card data for showing average result
    card_data = f'{df[df["Lokasi"] == "Jakarta"]["Title"].count()}'  # Top Job


    # Generate plot for Price
    fig_lokasi, ax_lokasi = plt.subplots(figsize=(16, 5))  # Adjust the width (16) and height (5) as needed
    df['Lokasi'].value_counts().plot(kind = 'barh', ax=ax_lokasi).invert_yaxis() 
    
    # Rendering plot for By IMDB Rating
    figfile_lokasi = BytesIO()
    plt.savefig(figfile_lokasi, format='png', transparent=True)
    figfile_lokasi.seek(0)
    figdata_png_lokasi = base64.b64encode(figfile_lokasi.getvalue())
    plot_result = str(figdata_png_lokasi)[2:-1]
    plt.close(fig_lokasi)

    return render_template('index.html',
                           card_data=card_data, # Pass the Average Price
                           plot_result=plot_result  # Pass the Price
                           )

if __name__ == "__main__":
    app.run(debug=True)
