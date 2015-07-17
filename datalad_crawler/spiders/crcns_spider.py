# -*- coding: utf-8 -*-
import os
import scrapy
import utils
from sys import exit
import pprint
import shelve



def printing(something):
    print '\n' + '#'*30
    print something
    #pprint.pprint(something)
    print '#'*30 + '\n'


printing(__name__)
#collected_data = {}
collected_data = shelve.open('./crcns.shlv', writeback=True)


class CrcnsSpider(scrapy.Spider):
    '''
    Output looks like this in the shelve:
    {'Data Sets':
        {'Visual cortex':   {'pvc-1': {'About pvc-1': <the html>,
                                       'Conditions': <the html>,
                                       'pvc-1 downloads at NERSC': <the data links>,
                                       'Other formats': <the html>,
                                      },
                             'pvc-2': {'About pvc-1': <the html>,
                                       'pvc-2 downloads at NERSC': <the data links>,
                                      },
                             'etc':   {'...',
                                      },
                            },
         'Auditory cortex': {'ac-1':  {'About': <the html>,
                                       'downloads at NERSC': <the data links>,
                                      },
                             'etc':   {'About': <the html>,
                                       'downloads at NERSC': <the data links>,
                                       'anything else': <the html>,
                                      },
                            },
         'Etc':             {'etc':   {'About': <the html>,
                                       'downloads at NERSC': <the data links>,
                                      },
                            },
        }
    }
    '''


    name = "crcns"     # NOTE uncomment this to make the spider work
    allowed_domains = ["crcns.org",     # this alone won't work b/c the ds download pages are different
                       "portal.nersc.gov"]
    start_urls = ['http://crcns.org/data-sets/']

    #start_urls = [
                  ##'http://crcns.org/data-sets/data-sets/vc/' 
                  ##'http://crcns.org/data-sets/data-sets/ac/' 
                  ##'http://crcns.org/data-sets/data-sets/hc/' 
                  ##'https://portal.nersc.gov/project/crcns/download/pvc-1/'
                  ##'https://portal.nersc.gov/project/crcns/download/cai-1/'
                 #]
    
    #to login, do something like these:
    #http://doc.scrapy.org/en/1.0/topics/spiders.html#scrapy.spiders.Spider.start_requests
    #http://doc.scrapy.org/en/1.0/topics/request-response.html#using-formrequest-from-response-to-simulate-a-user-login

    # to use proxy:
    #http://doc.scrapy.org/en/1.0/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpproxy


    def parse(self, response):
        if 'crcns.org' in response.url:
            resp_contents = response.xpath('//div[@id="content"]')

            h1_page_name = resp_contents.xpath('.//h1/text()').extract_first().strip()
            if not h1_page_name: 
                h1_page_name = resp_contents.xpath('.//h1/span/text()').extract_first().strip()
                if not h1_page_name:
                    exit("ERROR: The <h1> tag isn't being caught")
            h1_page_name= str(h1_page_name)

            ds = response.meta.get('dataset', collected_data)
            dataset_collecting = ds[h1_page_name] = {}

            contents_dts = resp_contents.xpath('.//dl/dt[@class=""]')
            if contents_dts:    # means there are links to follow
                for dt in contents_dts:
                    h_text = str(dt.xpath('.//a/text()').extract_first().strip())
                    href = dt.xpath('.//a/@href').extract_first()
                    full_url = response.urljoin(href)
                    #printing("H_TEXT: {} ---- FULL_URL: {}".format(h_text, full_url))

                    if "downloads at NERSC" in h_text:
                        # the href here will redirect to a portal.nersc.gov/crcns/download/ds_name page
                        dataset = dataset_collecting[h_text] = {}
                        request = scrapy.Request(full_url, callback=self.parse_nersc_ds_page, 
                                                 cookies={'crcns_nersc_download': utils.cookie},
                                                 meta={'dataset': dataset,
                                                      })
                        yield request
                    else:
                        yield scrapy.Request(full_url, callback=self.parse,
                                             meta={'ds_name': h_text, 
                                                   'dataset': dataset_collecting,
                                                  }) 

            else:   # means don't follow any links, but just grab the html(/or url) from the page
                dataset = response.meta['dataset']
                ds_name = response.meta['ds_name']
                dataset[ds_name] = response.url     # or response.body or resp_contents to get the html instead


        elif 'portal.nersc.gov' in response.url:
            #yield scrapy.Request(response.url, callback=self.parse_nersc_ds_page)
            printing("IN THE ELIF -- 'portal.nersc.gov' url found")

        else:
            printing("IN THE ELSE -- this shouldn't happen!")


    def parse_nersc_ds_page(self, response):
        if response.xpath('//form'):    # means we need to login to see the ds contents
            printing("NEED TO LOG IN\n" + response.url)

            yield scrapy.FormRequest.from_response(response,
                                    formdata={'username': utils.user, 
                                              'password': utils.pswd},
                                    meta={'url': response.url, 
                                          'dataset': response.meta['dataset'],
                                         }, 
                                    callback=self.parse_nersc_ds_page)

        elif "Logged in as" in response.xpath('//p').extract_first():
            #printing("ALEADY LOGGED IN")
            # NOTE response.url is not correct here after logging into a ds page; so would 
            # need to get the url from the original login page for the ds (the url in meta)
            
            dataset = response.meta['dataset']

            a_hrefs = response.xpath('//a')[1:]     # the first href is a link to logout
            for a_href in a_hrefs:
                href_path = a_href.xpath('.//@href').extract_first()
                href_text = a_href.xpath('.//text()').extract_first()
                full_url = response.urljoin(href_path)

                # FIXME should be a better way to check if the link goes to another subdirectory or is a file to download???
                # Alternatively, could figure out a way to check the byte size info is given for each href (only files 
                # have this info, not dirs); probably use a regrex to do this.
                h_root, h_ext = os.path.splitext(href_path)

                if href_text == '..': 
                    continue
                elif (not h_ext) and (not h_root.startswith('.')):   # then go into the href dir
                    request = scrapy.Request(full_url, callback=self.parse_nersc_ds_page)
                    request.meta['dataset'] = dataset[href_text] = {}
                    yield request
                #elif h_root.startswith('.'):
                    #exit("HIDDEN file or dir.")
                else:
                    dataset[href_text] = full_url 

        else:
            printing("ERROR: NOT PRESENTED WITH THE LOGIN FORM SCREEN AND/OR NOT ALREADY LOGGED IN")
            exit()


