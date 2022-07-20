import requests
import singer
import json
from time import sleep

LOGGER = singer.get_logger()

class BlingERPClient():

    def __init__(self, config):
        self.config = config


    def get_orders(self,start_time,end_time):

        # define request parameters
        params = {
            'filters': 'dataAlteracao['+start_time+' TO '+end_time+']',
            'apikey':self.config['api_token'],
            'historico':'true'}
        LOGGER.info("Request - Start Datetime: {0}, Finish Datetime: {1}".\
            format(start_time,end_time))

        page = 1
        more_pages = True

        # Iterate until API doesn't have more pages
        while more_pages == True:
            LOGGER.info("Pages: {}".format(page))
            url = "/".join([self.config['api_url'],'v2','pedidos','page='+str(page),'json'])         
            resp = requests.get(url=url, params=params)
            
            # if status code is not 200 raise errors
            if resp.status_code != 200:
                raise "Request Error. Status: {0}. Error: {1}".format(resp.status_code,resp.content)
            
            response = resp.json()

            if 'retorno' not in response:
                raise "Error parsing response. Key 'retorno' not available in API response."
            
            return_dict = response['retorno']

            if 'erros' in return_dict:
                more_pages = False
                break
            
            if 'pedidos' not in return_dict:
                raise "Error parsing response. Key 'pedidos' not available in API response."
            
            LOGGER.info("Page requested: {}".format(page))
            
            page = page + 1

            yield page, return_dict['pedidos']

    def get_invoices(self,start_time,end_time):

        # define request parameters
        params = {
            'filters': 'dataEmissao['+start_time+' TO '+end_time+']',
            'apikey':self.config['api_token']
        }
        if self.config.get('invoice_extra_filters'):
            params['filters'] += ';' + self.config.get('invoice_extra_filters')

        LOGGER.info("Request - Start Datetime: {0}, Finish Datetime: {1}".\
            format(start_time,end_time))

        page = 1
        more_pages = True

        # Iterate until API doesn't have more pages
        while more_pages:
            LOGGER.info("Pages: {}".format(page))
            url = "/".join([self.config['api_url'],'v2','notasfiscais','page='+str(page),'json'])         
            resp = requests.get(url=url, params=params)
            #TODO: replace this by singer rate limiting decorators
            sleep(2)  # enforce rate limiting
            
            # if status code is not 200 raise errors
            if resp.status_code != 200:
                raise "Request Error. Status: {0}. Error: {1}".format(resp.status_code,resp.content)
            
            response = resp.json()

            if 'retorno' not in response:
                raise "Error parsing response. Key 'retorno' not available in API response."
            
            return_dict = response['retorno']

            if 'erros' in return_dict:
                more_pages = False
                break
            
            if 'notasfiscais' not in return_dict:
                raise "Error parsing response. Key 'notasfiscais' not available in API response."
            
            LOGGER.info("Page requested: {}".format(page))
            
            page = page + 1

            yield page, return_dict['notasfiscais']
