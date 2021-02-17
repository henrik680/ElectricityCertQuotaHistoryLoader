#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import lxml.html as lh

from urllib.request import urlopen, Request

def table_to_dict(tr_elements):
       col = []
       # Since out first row is the header, data is stored on the second row onwards
       for j in range(1, len(tr_elements)):
              # T is our j'th row
              T = tr_elements[j]

              # i is the index of our column
              i = 0

              # Iterate through each element of the row
              for t in T.iterchildren():
                     data = t.text_content()
                     # Check if row is empty
                     if i > 0:
                            # Convert any numerical value to integers
                            try:
                                   data = int(data)
                            except:
                                   pass
                     # Append the data to the empty list of the i'th column
                     col[i][1].append(data)
                     # Increment i for the next column
                     i += 1
       return {title:column for (title,column) in col}



reg_url = 'https://www.energimyndigheten.se/fornybart/elcertifikatsystemet/om-elcertifikatsystemet/kvotnivaer/'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

#df_list = pd.read_html(io=reg_url, header=hdr)

#print(df_list)


#headers = {‘User-Agent’: ‘Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3’}
#reg_url = “https:XXXXOOOO"
req = Request(url=reg_url, headers=hdr)
html = urlopen(req).read()
doc = lh.fromstring(html)
#Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')
df=pd.DataFrame(table_to_dict(tr_elements))
print(df)