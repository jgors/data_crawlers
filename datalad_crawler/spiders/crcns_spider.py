# -*- coding: utf-8 -*-
import os
import sys
from sys import exit
import pprint
import shelve

import scrapy
from scrapy.shell import inspect_response

# FIXME this is just a hack to import this b/c i am not working in a package here
sys.path.append('/home/jgors/junk/datalad_junk/scrapy_testing/data_crawlers')
#import installation_tasks
import utils_for_scraping


# README
# -- currently, cookies are stored in xdg_config_home + '/datalad/cookies.db' (eg. linux, ~/.config/datalad/cookies.db)
# -- login info (username and password) are to be entered on the commandline if the above doesn't work  
#username = xxxxx
#password = xxxxx


def printing(something):
    print('\n' + '#'*30)
    print(something)
    #pprint.pprint(something)
    print('#'*30 + '\n')


#printing(__name__)
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



    #def start_requests(self):
        #start_url = 'https://portal.nersc.gov/project/crcns/download/pvc-1/'
        #return [scrapy.FormRequest(start_url,
                                   #formdata={'username': username, 'password': password},
                                   #callback=self.logged_in)]


    name = "crcns"     # NOTE this must be uncommented for the spider to work
    data_provider = name
    allowed_domains = ["crcns.org",     # this alone won't work b/c the ds download pages are hosted at nersc 
                       "portal.nersc.gov"]
    #start_urls = ['http://crcns.org/data-sets/']
    
    #to login, do something like these:
    #http://doc.scrapy.org/en/1.0/topics/spiders.html#scrapy.spiders.Spider.start_requests
    #http://doc.scrapy.org/en/1.0/topics/request-response.html#using-formrequest-from-response-to-simulate-a-user-login

    # to use proxy:
    #http://doc.scrapy.org/en/1.0/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpproxy


    #def __init__(self, start_url=None, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        super(CrcnsSpider, self).__init__(*args, **kwargs)
        # This is to specify the start url form the cmdline, like:
        # http://doc.scrapy.org/en/1.0/topics/spiders.html#spider-arguments
        # scrapy crawl crcns -a start_url='https://portal.nersc.gov/project/crcns/download/pvc-1/'
        #if start_url:
            #self.start_urls = [start_url] 
        #else:
            #self.start_urls = ['http://crcns.org/data-sets/']

        # Check if cookie for this site/spider exists: if so, use/try it,
        # if not, then just go with single dataset to generate the cookie to 
        # use on the whole site.
        self.cookies = cookies = utils_for_scraping.manage_cookies()
        printing(cookies)
        if self.data_provider not in cookies:
            printing("RUNNING CRAWLER WITH SINGLE DS FIRST TO GEN COOKIE.")
            self.start_urls = ['https://portal.nersc.gov/project/crcns/download/pvc-1/']
        else:
            self.start_urls = ['http://crcns.org/data-sets/']


    def parse(self, response):
        if 'crcns.org' in response.url:
            resp_contents = response.xpath('//div[@id="content"]')

            h1_page_name = resp_contents.xpath('.//h1/text()').extract_first().strip()
            if not h1_page_name: 
                h1_page_name = resp_contents.xpath('.//h1/span/text()').extract_first().strip()
                if not h1_page_name:
                    exit("ERROR: The <h1> tag isn't being caught")
            h1_page_name = str(h1_page_name)

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
                                                cookies=self.cookies[self.data_provider], # FIXME what if the cookie doesn't work?
                                                meta={'dataset': dataset,
                                                    }, 
                                                )
                        yield request
                    else:
                        yield scrapy.Request(full_url, callback=self.parse,
                                            meta={'ds_name': h_text, 
                                                'dataset': dataset_collecting,
                                                }) 

            else:   # means don't follow any links, but just grab the html(/or url) from the page
                dataset = response.meta['dataset']
                ds_name = response.meta['ds_name']
                dataset[ds_name] = {'url': response.url}     # or response.body or resp_contents to get the html instead
                #dataset[ds_name] = resp_contents#.xpath('.//h1')
                h2s = resp_contents.xpath('.//h2/text()').extract()
                if len(h2s):
                    dataset[ds_name]['h2s'] = h2s


        elif 'portal.nersc.gov' in response.url:
            printing("IN THE ELIF -- 'portal.nersc.gov' url found.")
            yield scrapy.Request(response.url, callback=self.parse_nersc_ds_page, meta={'dataset': {}})

        else:
            printing("IN THE ELSE -- this shouldn't happen b/c we restricted the allowed_domains!")


    def parse_nersc_ds_page(self, response):
        if response.xpath('//form'):    # means we need to login to see the ds contents
            printing("NEED TO LOG IN\n" + response.url)
            #user_and_password_dict = {'username': username, 'password': password}  
            user_and_password_dict = utils_for_scraping.get_user_credentials()

            #yield scrapy.FormRequest.from_response(response,
            form_request = scrapy.FormRequest.from_response(response,
                                    formdata=user_and_password_dict,
                                    meta={'url': response.url, 
                                          'dataset': response.meta['dataset'],
                                         }, 
                                    callback=self.parse_nersc_ds_page)

            #import pdb; pdb.set_trace()
            yield form_request

        elif "Logged in as" in response.xpath('//p').extract_first():
            printing("ALEADY LOGGED IN")
            # NOTE response.url is not correct here after logging into a ds page; so would 
            # need to get the url from the original login page for the ds (the url in meta)
            #inspect_response(response, self)

            #if 'Set-Cookie' in response.headers:
            if self.data_provider not in self.cookies:
                cookie_id, cookie = response.headers['Set-Cookie'].split('=')
                printing("SAVING COOKIE, NOW RERUN TO CRAWL SITE.")
                self.cookies[self.data_provider] = {cookie_id: cookie}
                self.cookies.close()
                return 
            #if 'Set-Cookie' in response.headers:
                #cookie_id, cookie = response.headers['Set-Cookie'].split('=')
                #cookies = utils_for_scraping.get_cookies()
                #if self.data_provider not in cookies:
                    #printing("SAVING COOKIE")
                    #utils_for_scraping.set_cookie({self.data_provider: {cookie_id: cookie}})
                    #printing("Now re-run the spider since the cookie has been generated.")
                    #return 
                
            
            dataset = response.meta['dataset']

            a_hrefs = response.xpath('//a')[1:]     # the first href is a link to logout
            for a_href in a_hrefs:
                href_path = a_href.xpath('.//@href').extract_first()
                href_text = a_href.xpath('.//text()').extract_first()
                full_url = response.urljoin(href_path)

                # FIXME should be a better way to check if the link goes to another subdirectory or is a file to download???
                # Alternatively, could figure out a way to check the byte size info is given for each href (only files 
                # have this info, not dirs); probably use a regex to do this.
                h_root, h_ext = os.path.splitext(href_path)

                if href_text == '..': 
                    continue
                elif (not h_ext) and (not h_root.startswith('.')):   # then go into the href dir
                    request = scrapy.Request(full_url, callback=self.parse_nersc_ds_page)
                    request.meta['dataset'] = dataset[href_text] = {}
                    #yield request
                    yield request
                #elif h_root.startswith('.'):
                    #exit("HIDDEN file or dir.")
                else:
                    dataset[href_text] = full_url 

        else:
            printing("ERROR: NOT PRESENTED WITH THE LOGIN FORM SCREEN AND/OR NOT ALREADY LOGGED IN")
            exit()


