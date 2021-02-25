import pandas as pd
import lxml.html as lh
import logging
import argparse
import json
from google.cloud import storage
from google.cloud.storage import Blob
from urllib.request import urlopen, Request

logging.getLogger().setLevel(logging.INFO)


def table_to_dict(tr_elements):
    # Create empty list
    col = []
    i = 0
    # For each row, store each first element (header) and an empty list
    for t in tr_elements[0]:
        i += 1
        name = t.text_content().strip()
        col.append((name, []))

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
    return {title: column for (title, column) in col}


def upload_blob_string(bucket_name, csvString, destination_blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = Blob(destination_blob_name, bucket)
    return blob.upload_from_string(
        data=csvString,
        content_type='text/csv')


def run(request):
    logging.info("Starting ElectricityCertQuotaHistoryLoader")
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='json with parameters')
    args = parser.parse_args()
    if request is None:
       logging.info('run(...): data=' + args.data)
       input_json = json.loads(str(args.data).replace("'", ""))
    else:
       input_json = request.get_json()
    logging.info("request.args: {}".format(input_json))
    bucket_name = input_json['bucket_target']
    reg_url = input_json['url']
    destination_blob_name = input_json['destination_blob_name']
    logging.info("\nbucket_name: {}\nreg_url: {}\ndestination_blob_name: {}".format(
       bucket_name, reg_url, destination_blob_name))
    hdr = {
       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    req = Request(url=reg_url, headers=hdr)
    html = urlopen(req).read()
    doc = lh.fromstring(html)
    # Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    df = pd.DataFrame(table_to_dict(tr_elements))
    csv_string = df.to_csv(index=False, sep=';')
    upload_blob_string(bucket_name, csv_string, destination_blob_name)
    logging.info("Uploaded size={} to bucket {} and {}".format(df.size, bucket_name, destination_blob_name))


if __name__ == '__main__':
    run(None)